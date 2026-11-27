"""`codeown init`: bật CodeOwn cho một repo.

- Claude Code: gộp hook vào .claude/settings.json (không ghi đè hook có sẵn, chạy 2 lần không nhân đôi)
- Cursor: gộp vào .cursor/hooks.json
- git: thêm vào hook post-commit (giữ nội dung cũ)
- .gitignore: thêm .codeown/
- .codeown/config.jsonl: tools, rules_only (mỗi lần init thêm một dòng, dòng cuối có hiệu lực)
Copilot / Codex: chưa làm (task.md, CP4).
"""
import json
import os
import stat
import sys

from . import events as E

MARK = "codeown"
ENTRY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codeown_cli.py")
SUPPORTED = ("claude_code", "cursor")


def _q(path):
    return '"%s"' % path.replace("\\", "/")


def hook_command(tool, python=None, entry=None):
    return "%s %s hook --tool=%s" % (_q(python or sys.executable), _q(entry or ENTRY), tool)


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _has_mark(obj):
    return MARK in json.dumps(obj)


def install_claude_code(repo, cmd):
    path = os.path.join(repo, ".claude", "settings.json")
    data = _load_json(path)
    hooks = data.setdefault("hooks", {})
    wanted = {
        "UserPromptSubmit": {"hooks": [{"type": "command", "command": cmd}]},
        "PostToolUse": {"matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash",
                        "hooks": [{"type": "command", "command": cmd}]},
        "Stop": {"hooks": [{"type": "command", "command": cmd}]},
    }
    for event, entry in wanted.items():
        lst = hooks.setdefault(event, [])
        lst[:] = [x for x in lst if not _has_mark(x)]  # bỏ bản CodeOwn cũ (đường dẫn có thể đã đổi)
        lst.append(entry)
    _write_json(path, data)
    return path


def install_cursor(repo, cmd):
    path = os.path.join(repo, ".cursor", "hooks.json")
    data = _load_json(path)
    data.setdefault("version", 1)
    hooks = data.setdefault("hooks", {})
    for event in ("beforeSubmitPrompt", "afterFileEdit", "afterShellExecution", "stop"):
        lst = hooks.setdefault(event, [])
        lst[:] = [x for x in lst if not _has_mark(x)]
        lst.append({"command": cmd})
    _write_json(path, data)
    return path


def install_git(repo, cmd):
    rel = E.git(repo, "rev-parse", "--git-path", "hooks")
    if rel is None:
        return None
    hooks_dir = rel.strip()
    hooks_dir = hooks_dir if os.path.isabs(hooks_dir) else os.path.join(repo, hooks_dir)
    os.makedirs(hooks_dir, exist_ok=True)
    path = os.path.join(hooks_dir, "post-commit")
    block = "# >>> codeown\n%s || true\n# <<< codeown\n" % cmd
    try:
        with open(path, encoding="utf-8") as f:
            old = f.read()
    except OSError:
        old = "#!/bin/sh\n"
    if "# >>> codeown" in old:
        start, end = old.index("# >>> codeown"), old.index("# <<< codeown") + len("# <<< codeown\n")
        new = old[:start] + block + old[end:]
    else:
        new = old.rstrip("\n") + "\n" + block
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def ensure_gitignore(repo):
    path = os.path.join(repo, ".gitignore")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        lines = []
    if any(ln.strip() in (".codeown/", ".codeown", "/.codeown/") for ln in lines):
        return False
    with open(path, "a", encoding="utf-8") as f:
        if lines and lines[-1].strip():
            f.write("\n")
        f.write("# CodeOwn: log chỉ nằm trên máy, không commit\n.codeown/\n")
    return True


def init(repo, tools=("claude_code",), rules_only=False, python=None, entry=None):
    repo = os.path.abspath(repo)
    written, skipped = [], []
    for tool in tools:
        cmd = hook_command(tool, python, entry)
        if tool == "claude_code":
            written.append(install_claude_code(repo, cmd))
        elif tool == "cursor":
            written.append(install_cursor(repo, cmd))
        else:
            skipped.append(tool)
    git_hook = install_git(repo, hook_command("git", python, entry))
    if git_hook:
        written.append(git_hook)
    gi = ensure_gitignore(repo)
    os.makedirs(E.codeown_dir(repo), exist_ok=True)
    E.append_jsonl(os.path.join(E.codeown_dir(repo), "config.jsonl"),
                   {"ts": E.now_iso(), "tools": list(tools), "rules_only": bool(rules_only)})
    E.save_state(repo, {"enabled": True})
    rel = [os.path.relpath(p, repo).replace("\\", "/") for p in written]
    return {"hooks_written": rel, "gitignore_updated": gi, "not_supported_yet": skipped,
            "rules_only": bool(rules_only)}


def load_config(repo):
    d = E.codeown_dir(repo)
    return E.load_jsonl_merged(os.path.join(d, "config.jsonl"), os.path.join(d, "config.json"))
