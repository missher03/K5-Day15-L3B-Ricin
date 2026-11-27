"""Công cụ của CodeOwn — phần C (Lê Thành Nguyên). Khớp bảng công cụ ở spec.md §4 / docs/design.md §6.

Mỗi công cụ là một hàm có @tool (khung tự ghi vào trace). Docstring ghi: tên · input · output · có tác động ra ngoài không.

Dữ liệu: khi chạy eval / simulate, mọi mã (task_id, diff_id, session_id) trỏ vào một mẫu trong data/samples/
(tra ở data/samples/index.json). Khi dùng thật, lõi `codeown` của A / B đọc thư mục `.codeown/` của repo người dùng.
Quy ước nối hai bên: trước khi gọi một hàm của lõi theo task_id, công cụ đặt biến môi trường
    CODEOWN_HOME = thư mục của mẫu   (chứa events.jsonl, diff.patch, meta.json)
nên lõi chỉ cần đọc `$CODEOWN_HOME/events.jsonl` (mặc định `.codeown/`) là chạy được trên cả hai.

Không công cụ nào được đọc truth.json (đáp án của bộ câu thử) — xem _safe_path.
"""
import importlib
import json
import os
import re
import subprocess
import sys

from tracing import tool, TOOLS  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, "data", "samples")
DOCS = os.path.join(ROOT, "data", "docs")
FORBIDDEN = {"truth.json"}
SNIPPET_TIMEOUT = 5


# ================================================================ tiện ích (không phải công cụ)

def _index():
    with open(os.path.join(SAMPLES, "index.json"), encoding="utf-8") as f:
        return json.load(f)


def sample_dir(any_id):
    """task_id / diff_id / session_id / tên repo mẫu → thư mục mẫu, hoặc None."""
    idx = _index()
    for kind in ("tasks", "diffs", "sessions", "repos"):
        if any_id in idx.get(kind, {}):
            return os.path.join(SAMPLES, *idx[kind][any_id].split("/"))
    return None


def _need_dir(any_id):
    d = sample_dir(any_id)
    if not d:
        raise ValueError("không có mẫu nào mang mã %r (xem data/samples/index.json)" % any_id)
    return d


def _safe_path(path):
    """Chỉ cho đọc file trong data/samples/*/repo/, không cho đọc đáp án."""
    full = os.path.abspath(os.path.join(SAMPLES, path))
    if not full.startswith(SAMPLES + os.sep):
        raise PermissionError("chỉ đọc được file trong data/samples/")
    if os.path.basename(full) in FORBIDDEN or os.sep + "repo" + os.sep not in full[len(SAMPLES):]:
        raise PermissionError("chỉ đọc được code trong data/samples/<mẫu>/repo/")
    return full


def load_meta(any_id):
    with open(os.path.join(_need_dir(any_id), "meta.json"), encoding="utf-8") as f:
        return json.load(f)


def core(name):
    """Module của lõi codeown (A / B viết) nếu đã có, không có thì None — agent.py rẽ sang nhánh giả."""
    try:
        return importlib.import_module("codeown." + name)
    except ImportError:
        return None


def use_sample(any_id):
    """Trỏ lõi vào mẫu (CODEOWN_HOME). Trả thư mục mẫu."""
    d = _need_dir(any_id)
    os.environ["CODEOWN_HOME"] = d
    return d


def parse_patch(text):
    """unified diff → (dòng thêm [{file, line, code}], dòng xoá [{file, code}])."""
    added, removed, path, new_no = [], [], None, 0
    for raw in text.splitlines():
        if raw.startswith("+++ "):
            path = raw[4:].strip()
            path = path[2:] if path.startswith("b/") else path
            continue
        if raw.startswith("--- ") or raw.startswith("diff --git") or raw.startswith("new file mode"):
            continue
        m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
        if m:
            new_no = int(m.group(1))
            continue
        if path is None:
            continue
        if raw.startswith("+"):
            added.append({"file": path, "line": new_no, "code": raw[1:]})
            new_no += 1
        elif raw.startswith("-"):
            removed.append({"file": path, "code": raw[1:]})
        else:
            new_no += 1
    return added, removed


# ================================================================ công cụ

@tool
def read_diff(task_id: str) -> dict:
    """read_diff · input: task_id hoặc diff_id · output: {"task_id", "files", "lines": [{file, line, code, label}],
    "removed": [{file, code}]} — label lấy từ attribution của A nếu đã có, chưa có thì "chua_gan".
    Không tác động ra ngoài."""
    d = use_sample(task_id)
    meta = load_meta(task_id)
    with open(os.path.join(d, "diff.patch"), encoding="utf-8") as f:
        added, removed = parse_patch(f.read())
    labels = {}
    res = monitor_offline(task_id)
    if res is not None:
        labels = {(l["file"], l["line"]): l["label"] for l in res.get("lines", [])}
    for l in added:
        l["label"] = labels.get((l["file"], l["line"]), "chua_gan")
    return {"task_id": meta["task_id"], "diff_id": meta.get("diff_id"), "files": sorted({l["file"] for l in added}),
            "lines": added, "removed": removed}


@tool
def read_file(path: str, start: int = 1, end: int = 0) -> dict:
    """read_file · input: đường dẫn tính từ data/samples/ (vd "repo03_auth_login/repo/auth.py"), dòng đầu, dòng cuối
    (0 = hết file) · output: {"path", "start", "end", "code"} có số dòng. Không tác động ra ngoài."""
    full = _safe_path(path)
    with open(full, encoding="utf-8") as f:
        lines = f.read().splitlines()
    start = max(int(start or 1), 1)
    end = len(lines) if not end else min(int(end), len(lines))
    code = "\n".join("%4d  %s" % (k, lines[k - 1]) for k in range(start, end + 1))
    return {"path": path, "start": start, "end": end, "code": code}


def _sample_events(task_id):
    """events.jsonl của mẫu (đã có use_sample). Đọc qua events.load_jsonl của A nếu có."""
    path = os.path.join(_need_dir(task_id), "events.jsonl")
    events_mod = core("events")
    if events_mod is not None and hasattr(events_mod, "load_jsonl"):
        return events_mod.load_jsonl(path)
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _sample_patch(task_id):
    path = os.path.join(_need_dir(task_id), "diff.patch")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def monitor_offline(task_id):
    """Chạy Monitor của A trên một mẫu (không git): gán dòng + DI + nhắc.
    → kết quả monitor.analyze_offline (có "lines", "pending_nudge"), hoặc None nếu lõi chưa có.
    "now" = thời điểm sự kiện cuối của phiên, để luật nhắc tính như lúc vừa commit."""
    use_sample(task_id)
    mon, ev_mod = core("monitor"), core("events")
    if mon is None or ev_mod is None:
        return None
    evs = _sample_events(task_id)
    now = ev_mod.parse_ts(evs[-1]["ts"]) if evs else None
    return mon.analyze_offline(evs, _sample_patch(task_id), task_id=load_meta(task_id)["task_id"],
                               mode="rules", now=now)


@tool
def get_events(task_id: str) -> list:
    """get_events · input: task_id / session_id · output: danh sách sự kiện (dict) theo hợp đồng task.md 0.2.
    Không tác động ra ngoài."""
    use_sample(task_id)
    return _sample_events(task_id)


@tool
def compute_dependence(task_id: str):
    """compute_dependence · input: task_id / session_id · output: {"di", "features": {f1..f5}, "stats"} do lõi A
    tính (code, không AI; prompt phân loại bằng luật); lõi chưa có thì None. Không tác động ra ngoài."""
    res = monitor_offline(task_id)
    if res is None:
        return None
    return {"di": res["di"], "features": res["features"], "stats": res["stats"]}


_PRELUDE = r'''
import importlib.util, json, socket, sys
def _blocked(*a, **k):
    raise PermissionError("run_snippet: không được dùng mạng")
socket.socket = _blocked
socket.create_connection = _blocked
for _m in ("requests", "urllib3", "httpx", "aiohttp"):
    sys.modules[_m] = None
path, func, arg = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
spec = importlib.util.spec_from_file_location("snippet", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fn = getattr(mod, func)
res = fn(*arg) if isinstance(arg, list) else (fn(**arg) if isinstance(arg, dict) else fn(arg))
print(json.dumps({"result": res}, ensure_ascii=False, default=repr))
'''


@tool
def run_snippet(path: str, func: str, input=None) -> dict:
    """run_snippet · input: file Python trong data/samples/<mẫu>/repo/, tên hàm, đối số (list = *args, dict = **kwargs)
    · output: {"ok", "result" | "error"} · chạy trong tiến trình con, timeout 5 giây, chặn socket / requests,
    thư mục làm việc tạm. Không tác động ra ngoài."""
    full = _safe_path(path)
    if not full.endswith(".py"):
        return {"ok": False, "error": "chỉ chạy được file .py"}
    workdir = os.path.join(ROOT, ".codeown-tmp")
    os.makedirs(workdir, exist_ok=True)
    try:
        p = subprocess.run([sys.executable, "-I", "-B", "-c", _PRELUDE, full, func, json.dumps(input, ensure_ascii=False)],
                           capture_output=True, text=True, encoding="utf-8", timeout=SNIPPET_TIMEOUT, cwd=workdir)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "quá %d giây" % SNIPPET_TIMEOUT}
    if p.returncode != 0:
        last = (p.stderr.strip().splitlines() or ["lỗi không rõ"])[-1]
        return {"ok": False, "error": last[:300]}
    try:
        return {"ok": True, "result": json.loads(p.stdout.strip().splitlines()[-1])["result"]}
    except (ValueError, IndexError, KeyError):
        return {"ok": False, "error": "không đọc được kết quả: " + p.stdout[:200]}


def _doc_pages():
    pages = []
    if not os.path.isdir(DOCS):
        return pages
    for name in sorted(os.listdir(DOCS)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(DOCS, name), encoding="utf-8") as f:
            text = f.read()
        link = re.search(r"^link:\s*(\S+)", text, re.M)
        title = re.search(r"^#\s*(.+)", text, re.M)
        body = re.sub(r"^(link|xem|nguon):.*$", "", text, flags=re.M)
        pages.append({"page": name, "title": title.group(1).strip() if title else name,
                      "link": link.group(1) if link else "", "text": body.strip()})
    return pages


def _words(text):
    return set(re.findall(r"\w+", text.lower()))


@tool
def search_docs(query: str, k: int = 3) -> list:
    """search_docs · input: từ khoá / câu hỏi · output: ≤k đoạn [{"page", "title", "link", "text"}] từ bản docs offline
    data/docs/*.md, xếp theo số từ trùng. Không mạng, không tác động ra ngoài."""
    q = _words(query)
    scored = []
    for p in _doc_pages():
        paras = [x.strip() for x in p["text"].split("\n\n") if x.strip()]
        for para in paras:
            s = len(q & _words(para + " " + p["title"]))
            if s:
                scored.append((s, p, para))
    scored.sort(key=lambda x: -x[0])
    out, seen = [], set()
    for s, p, para in scored:
        if p["page"] in seen:
            continue
        seen.add(p["page"])
        out.append({"page": p["page"], "title": p["title"], "link": p["link"], "text": para[:600]})
        if len(out) >= k:
            break
    return out


@tool
def write_ledger(entry: dict, confirmed: bool = False) -> dict:
    """write_ledger · input: {"task_id", "concept", "label", ...}, confirmed · output: {"ok", "draft"}.
    CÓ tác động ra ngoài (ghi Sổ kiến thức của chính người dùng) → mặc định chỉ trả BẢN NHÁP; chỉ ghi khi
    confirmed=True, tức người dùng đã bấm Lưu. Ghi qua ledger.py của B nếu đã có."""
    if not confirmed:
        return {"ok": False, "draft": entry, "note": "bản nháp — chờ người dùng bấm Lưu"}
    ledger = core("ledger")
    if ledger is not None:
        ledger.save(entry["task_id"], [entry])
        return {"ok": True, "draft": None}
    home = os.environ.get("CODEOWN_HOME") or os.path.join(os.getcwd(), ".codeown")
    os.makedirs(home, exist_ok=True)
    with open(os.path.join(home, "ledger.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"ok": True, "draft": None}
