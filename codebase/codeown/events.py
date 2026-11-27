"""Đọc / ghi .codeown/events.jsonl (task.md mục 0.2). Mọi phần khác đọc sự kiện qua đây.

Một dòng sự kiện:
  id, ts, task_id, tool, event, session_id, model, branch, commit, prompt, file, line_hashes, meta
- event ∈ EVENT_TYPES
- prompt cắt ≤1000 ký tự, đã che bí mật
- line_hashes = sha1(dòng.strip()) của các dòng có nội dung
- meta.lines: chữ của các dòng AI ghi (chỉ nằm trên máy người dùng, cần để so độ giống khi gán dòng)
"""
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess

EVENT_TYPES = ("prompt", "ai_edit", "ai_bash", "ai_turn_end", "commit", "nudge", "manual_mark")
FIELDS = ("id", "ts", "task_id", "tool", "event", "session_id", "model", "branch", "commit",
          "prompt", "file", "line_hashes", "meta")
PROMPT_MAX = 1000
DIR_NAME = ".codeown"

# --- che bí mật ---------------------------------------------------------------
_SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    re.compile(r"xox[abpr]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}"),  # JWT
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
]
_KV_SECRET = re.compile(
    r"(?i)\b([A-Za-z0-9_]*(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|mat_khau|matkhau))"
    r"(\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,;]+)")
REDACTED = "[ĐÃ CHE]"


def redact(text):
    """Che API key, token, mật khẩu trong chuỗi. Không phải chuỗi thì trả nguyên."""
    if not isinstance(text, str) or not text:
        return text
    out = text
    for pat in _SECRET_PATTERNS:
        out = pat.sub(REDACTED, out)
    out = _KV_SECRET.sub(lambda m: m.group(1) + m.group(2) + REDACTED, out)
    return out


# --- hash dòng ------------------------------------------------------------------
_TRIVIAL = re.compile(r"^[\s()\[\]{};,]*$")


def is_trivial(line):
    """Dòng trống hoặc chỉ có dấu ngoặc / chấm phẩy: không dùng để gán AI / người (task.md mục A)."""
    return bool(_TRIVIAL.match(line))


def line_hash(line):
    return hashlib.sha1(line.strip().encode("utf-8")).hexdigest()


def meaningful_lines(text):
    """Các dòng có nội dung (đã strip), giữ thứ tự."""
    if not text:
        return []
    return [ln.strip() for ln in text.splitlines() if not is_trivial(ln)]


# --- đường dẫn, git, task ---------------------------------------------------------
def git(repo, *args):
    """Chạy git, trả stdout (str) hoặc None nếu lỗi."""
    try:
        res = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return res.stdout if res.returncode == 0 else None


def find_repo(start=None):
    """Thư mục gốc repo git chứa `start` (mặc định cwd). Không có git thì trả chính `start`."""
    start = os.path.abspath(start or os.environ.get("CODEOWN_REPO") or os.getcwd())
    top = git(start, "rev-parse", "--show-toplevel")
    return os.path.normpath(top.strip()) if top else start


def codeown_dir(repo):
    return os.path.join(repo, DIR_NAME)


def events_path(repo):
    return os.path.join(codeown_dir(repo), "events.jsonl")


def current_branch(repo):
    # symbolic-ref chạy được cả khi repo chưa có commit nào (rev-parse thì lỗi)
    out = git(repo, "symbolic-ref", "--short", "-q", "HEAD") or git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    return out.strip() if out and out.strip() else None


def _slug(text):
    s = re.sub(r"[^A-Za-z0-9]+", "-", text or "").strip("-").lower()
    return s[:40] or "no-branch"


def load_jsonl_merged(path, legacy_json=None):
    """File .jsonl dạng "mỗi dòng một lần cập nhật": gộp các dòng, dòng sau đè dòng trước.
    Chưa có file .jsonl mà có file .json cũ (bản trước) thì đọc file cũ."""
    rows = load_jsonl(path)
    if not rows and legacy_json and os.path.exists(legacy_json):
        try:
            with open(legacy_json, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}
    merged = {}
    for row in rows:
        merged.update({k: v for k, v in row.items() if k != "ts"})
    return merged


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_state(repo):
    d = codeown_dir(repo)
    return load_jsonl_merged(os.path.join(d, "state.jsonl"), os.path.join(d, "state.json"))


def save_state(repo, updates):
    """Ghi thêm một dòng vào .codeown/state.jsonl (chỉ các khoá thay đổi)."""
    append_jsonl(os.path.join(codeown_dir(repo), "state.jsonl"), dict({"ts": now_iso()}, **updates))


def current_task_id(repo, now=None):
    """task_id = ngày + tên nhánh, trừ khi người dùng đã chạy `codeown task new` (lưu ở state.jsonl)."""
    state = load_state(repo)
    if state.get("task_id"):
        return state["task_id"]
    now = now or _dt.datetime.now()
    return "t_%s_%s" % (now.strftime("%Y%m%d"), _slug(current_branch(repo)))


def new_task(repo, name=None, now=None):
    """Bắt đầu task mới: ghi task_id + commit gốc (để diff của task tính từ đây)."""
    now = now or _dt.datetime.now()
    tid = "t_%s_%s" % (now.strftime("%Y%m%d_%H%M"), _slug(name or current_branch(repo)))
    head = git(repo, "rev-parse", "HEAD")
    upd = {"task_id": tid, "base_commit": head.strip() if head else None,
           "started": now.astimezone().isoformat(timespec="seconds")}
    save_state(repo, upd)
    return upd


# --- ghi / đọc --------------------------------------------------------------------
def now_iso():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def parse_ts(ts):
    try:
        return _dt.datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def _next_id(path):
    try:
        with open(path, "rb") as f:
            n = sum(1 for _ in f)
    except OSError:
        n = 0
    return "ev_%06d" % (n + 1)


def make_event(event, **kw):
    if event not in EVENT_TYPES:
        raise ValueError("event không hợp lệ: %r" % event)
    ev = {k: None for k in FIELDS}
    ev.update({"event": event, "line_hashes": [], "meta": {}})
    ev.update({k: v for k, v in kw.items() if k in FIELDS})
    if ev["prompt"] is not None:
        ev["prompt"] = redact(str(ev["prompt"]))[:PROMPT_MAX]
    if ev["meta"].get("lines"):
        ev["meta"]["lines"] = [redact(x) for x in ev["meta"]["lines"]]
    if ev["meta"].get("command"):
        ev["meta"]["command"] = redact(ev["meta"]["command"])[:PROMPT_MAX]
    return ev


def append_event(repo, ev):
    """Ghi một sự kiện (dict theo make_event). Tự điền id, ts, task_id, branch nếu thiếu. Trả lại sự kiện."""
    path = events_path(repo)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ev = dict(ev)
    ev["id"] = ev.get("id") or _next_id(path)
    ev["ts"] = ev.get("ts") or now_iso()
    ev["branch"] = ev.get("branch") or current_branch(repo)
    ev["task_id"] = ev.get("task_id") or current_task_id(repo)
    append_jsonl(path, ev)
    return ev


def load_jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue  # bỏ dòng hỏng, không làm sập Monitor
    except OSError:
        pass
    return out


def read_events(repo, task_id=None):
    """Mọi sự kiện (theo thứ tự ghi) của một task; task_id=None → tất cả."""
    evs = load_jsonl(events_path(repo))
    return [e for e in evs if task_id is None or e.get("task_id") == task_id]
