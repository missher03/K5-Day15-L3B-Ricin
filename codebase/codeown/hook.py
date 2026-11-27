"""`codeown hook --tool=<tên>`: đọc JSON từ stdin của hook, ghi MỘT dòng vào .codeown/events.jsonl.

Hỗ trợ:
  claude_code  UserPromptSubmit · PostToolUse (Edit / Write / MultiEdit / NotebookEdit / Bash) · Stop
  cursor       beforeSubmitPrompt · afterFileEdit · afterShellExecution · stop
  git          post-commit (không có stdin)
  khác         đoán theo trường: prompt / file_path + content|new_string / command

Không bao giờ làm hỏng công cụ của người dùng: mọi lỗi bị nuốt, thoát mã 0.
"""
import json
import os
import sys

from . import events as E

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "str_replace_based_edit_tool"}


def _rel(repo, path):
    if not path:
        return None
    p = os.path.abspath(os.path.join(repo, path)) if not os.path.isabs(path) else os.path.abspath(path)
    try:
        rel = os.path.relpath(p, repo)
    except ValueError:  # ổ đĩa khác trên Windows
        return p.replace("\\", "/")
    return rel.replace("\\", "/")


def _edit_text(tool_input):
    """Chữ code mới mà AI ghi, từ input của công cụ sửa file."""
    ti = tool_input or {}
    parts = []
    for key in ("content", "new_string", "new_str", "file_text", "new_source"):
        if isinstance(ti.get(key), str):
            parts.append(ti[key])
    for ed in ti.get("edits") or []:
        if isinstance(ed, dict):
            for key in ("new_string", "new_str", "new_text"):
                if isinstance(ed.get(key), str):
                    parts.append(ed[key])
    return "\n".join(parts)


def _ai_edit(repo, tool, payload, file_path, text):
    lines = E.meaningful_lines(text)
    return E.make_event("ai_edit", tool=tool, session_id=payload.get("session_id") or payload.get("conversation_id"),
                        model=payload.get("model"), file=_rel(repo, file_path),
                        line_hashes=[E.line_hash(x) for x in lines], meta={"lines": lines})


def _prompt(tool, payload):
    from .classifier import classify_rules
    text = payload.get("prompt") or payload.get("user_prompt") or ""
    return E.make_event("prompt", tool=tool, session_id=payload.get("session_id") or payload.get("conversation_id"),
                        model=payload.get("model"), prompt=text,
                        meta={"label_rules": classify_rules(text)})


def event_from_payload(repo, tool, payload):
    """payload (dict từ stdin) → sự kiện, hoặc None nếu không cần ghi."""
    name = payload.get("hook_event_name") or payload.get("hookEventName") or ""
    sid = payload.get("session_id") or payload.get("conversation_id")

    if tool == "claude_code":
        if name == "UserPromptSubmit":
            return _prompt(tool, payload)
        if name == "PostToolUse":
            tname = payload.get("tool_name") or ""
            ti = payload.get("tool_input") or {}
            if tname in EDIT_TOOLS:
                return _ai_edit(repo, tool, payload, ti.get("file_path") or ti.get("notebook_path") or ti.get("path"),
                                _edit_text(ti))
            if tname == "Bash":
                return E.make_event("ai_bash", tool=tool, session_id=sid, meta={"command": ti.get("command") or ""})
            return None
        if name in ("Stop", "SubagentStop"):
            return E.make_event("ai_turn_end", tool=tool, session_id=sid)
        return None

    if tool == "cursor":
        if name == "beforeSubmitPrompt":
            return _prompt(tool, payload)
        if name == "afterFileEdit":
            return _ai_edit(repo, tool, payload, payload.get("file_path"), _edit_text(payload))
        if name in ("afterShellExecution", "beforeShellExecution"):
            return E.make_event("ai_bash", tool=tool, session_id=sid, meta={"command": payload.get("command") or ""})
        if name == "stop":
            return E.make_event("ai_turn_end", tool=tool, session_id=sid)
        return None

    # công cụ khác (Copilot, Codex…): đoán theo trường
    if payload.get("prompt") or payload.get("user_prompt"):
        return _prompt(tool, payload)
    fp = payload.get("file_path") or (payload.get("tool_input") or {}).get("file_path")
    if fp:
        return _ai_edit(repo, tool, payload, fp, _edit_text(payload.get("tool_input") or payload))
    cmd = payload.get("command") or (payload.get("tool_input") or {}).get("command")
    if cmd:
        return E.make_event("ai_bash", tool=tool, session_id=sid, meta={"command": cmd})
    return None


def commit_event(repo):
    head = E.git(repo, "rev-parse", "HEAD")
    if not head:
        return None
    sha = head.strip()
    msg = (E.git(repo, "log", "-1", "--format=%s", sha) or "").strip()
    files = [f for f in (E.git(repo, "show", "--name-only", "--format=", sha) or "").splitlines() if f]
    return E.make_event("commit", tool="git", commit=sha, meta={"message": E.redact(msg)[:300], "files": files})


def read_stdin(stdin=None):
    """Đọc stdin dạng BYTE rồi giải mã UTF-8. Trên Windows sys.stdin mặc định dùng bảng mã của máy
    (cp1252 / cp1258) nên "chào bạn" thành "chĂ o báº¡n" nếu đọc kiểu text."""
    if stdin is not None:
        return stdin.read()
    data = sys.stdin.buffer.read()
    for enc in ("utf-8-sig", "utf-16"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def run(tool, stdin=None, repo=None):
    """Điểm vào của hook. Trả sự kiện đã ghi (hoặc None)."""
    try:
        if tool == "git":
            repo = repo or E.find_repo()
            ev = commit_event(repo)
        else:
            raw = read_stdin(stdin)
            payload = json.loads(raw) if raw.strip() else {}
            repo = repo or E.find_repo(payload.get("cwd") or (payload.get("workspace_roots") or [None])[0])
            ev = event_from_payload(repo, tool, payload)
            if tool == "cursor" and payload.get("hook_event_name") == "beforeSubmitPrompt":
                sys.stdout.write('{"continue": true}')
        if ev is None:
            return None
        if tool == "git" or E.load_state(repo).get("enabled", True):
            ev = E.append_event(repo, ev)
            if tool == "git":
                from .monitor import write_summary
                write_summary(repo, ev.get("task_id"), ev.get("commit"))
            return ev
    except Exception:  # noqa: BLE001 — hook không được làm hỏng công cụ
        if os.environ.get("CODEOWN_DEBUG"):
            raise
    return None
