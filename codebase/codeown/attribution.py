"""Gán nhãn từng dòng mới trong diff của task (task.md mục 0.3).

  ai_giu_nguyen  dòng trùng hash một dòng AI đã ghi (sự kiện ai_edit)
  ai_da_sua      giống ≥ SIMILAR (difflib) với một dòng AI đã ghi
  nguoi_viet     còn lại

Bỏ dòng trống / chỉ có dấu ngoặc (events.is_trivial).
Phần thuần (không git) tách riêng để test: parse_patch, attribute_lines.
"""
import difflib
import fnmatch
import re

from . import events as E

SIMILAR = 0.6          # cùng file
SIMILAR_OTHER_FILE = 0.8  # dòng AI ở file khác (code bị chuyển file): chặt hơn để khỏi nhận nhầm
LABELS = ("ai_giu_nguyen", "ai_da_sua", "nguoi_viet")
# File không tính khi gán dòng (không phải code người dùng tự viết hay AI viết cho task):
#  - file CodeOwn tự sinh khi `init`: cấu hình hook của công cụ AI, .gitignore, .codeown/
#  - cấu hình editor, file khoá phụ thuộc (do trình quản lý gói sinh), code đã nén
#  - tài liệu (.md / .txt / .rst): là chữ, không phải code; Check cũng bỏ qua diff chỉ có docs
# Mẫu có "/" so với cả đường dẫn, không có "/" so với tên file. Thêm / bỏ qua .codeown/config.jsonl:
#   {"ignore": ["migrations/*", "*.csv"]}  ·  {"unignore": ["*.md"]}
DEFAULT_IGNORE = (
    ".codeown/*", ".claude/*", ".cursor/*", ".codex/*", ".github/hooks/*", ".vscode/*", ".idea/*",
    ".gitignore", ".gitattributes",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "uv.lock",
    "composer.lock", "Gemfile.lock", "Cargo.lock", "go.sum", "*.lock",
    "*.min.js", "*.min.css", "*.map",
    "*.md", "*.markdown", "*.rst", "*.txt", "LICENSE", "LICENSE.*",
)


def ignore_patterns(config=None):
    config = config or {}
    unignore = set(config.get("unignore") or [])
    return [p for p in DEFAULT_IGNORE if p not in unignore] + list(config.get("ignore") or [])


def is_ignored(path, patterns):
    path = _norm(path)
    base = path.rsplit("/", 1)[-1]
    for pat in patterns:
        if "/" in pat:
            if fnmatch.fnmatchcase(path, pat):
                return True
        elif fnmatch.fnmatchcase(base, pat):
            return True
    return False


_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parse_patch(patch):
    """unified diff → [{"file", "line", "code"}] cho các dòng THÊM (bỏ dòng trơ)."""
    out, file, new_line = [], None, 0
    for raw in (patch or "").splitlines():
        if raw.startswith("+++ "):
            path = raw[4:].strip()
            file = None if path == "/dev/null" else (path[2:] if path.startswith("b/") else path)
            continue
        if raw.startswith("--- ") or raw.startswith("diff --git") or raw.startswith("index "):
            continue
        m = _HUNK.match(raw)
        if m:
            new_line = int(m.group(1))
            continue
        if file is None:
            continue
        if raw.startswith("+"):
            code = raw[1:]
            if not E.is_trivial(code):
                out.append({"file": file, "line": new_line, "code": code})
            new_line += 1
        elif raw.startswith("-"):
            continue
        elif raw.startswith("\\"):
            continue  # "\ No newline at end of file"
        else:
            new_line += 1
    return out


def parse_removed(patch):
    """unified diff → [{"file", "code"}] cho các dòng XOÁ (bỏ dòng trơ) — để Examiner nhận diff chỉ đổi định dạng / tên."""
    out, file, in_hunk = [], None, False
    for raw in (patch or "").splitlines():
        if raw.startswith("diff --git"):
            in_hunk = False
            continue
        if not in_hunk and raw.startswith("--- "):
            path = raw[4:].strip()
            file = None if path == "/dev/null" else (path[2:] if path.startswith("a/") else path)
            continue
        if _HUNK.match(raw):
            in_hunk = True
            continue
        if in_hunk and file is not None and raw.startswith("-") and not E.is_trivial(raw[1:]):
            out.append({"file": file, "code": raw[1:]})
    return out


def ai_lines_from_events(evs):
    """Từ sự kiện ai_edit → (tập hash, {file: [chữ dòng]})."""
    hashes, by_file = set(), {}
    for ev in evs:
        if ev.get("event") != "ai_edit":
            continue
        hashes.update(ev.get("line_hashes") or [])
        lines = (ev.get("meta") or {}).get("lines") or []
        by_file.setdefault(_norm(ev.get("file")), []).extend(lines)
    return hashes, by_file


def _norm(path):
    path = (path or "").replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def _best_match(code, candidates, floor=SIMILAR):
    """→ (tỉ lệ giống cao nhất, dòng AI khớp nhất)."""
    code = code.strip()
    best, best_line = 0.0, None
    sm = difflib.SequenceMatcher(autojunk=False)
    sm.set_seq2(code)
    for cand in candidates:
        sm.set_seq1(cand)
        if sm.real_quick_ratio() < floor or sm.quick_ratio() < floor:
            continue
        r = sm.ratio()
        if r > best:
            best, best_line = r, cand
            if best >= 0.999:
                break
    return best, best_line


def attribute_lines(added, ai_hashes, ai_by_file):
    """Gán nhãn cho danh sách dòng thêm. Ưu tiên so với dòng AI cùng file, rồi mới tới file khác.
    Dòng AI có thêm "ai_hash" = hash của dòng AI gốc (để đo f4: AI ghi lúc nào)."""
    all_ai = [ln for lines in ai_by_file.values() for ln in lines]
    out = []
    for item in added:
        code = item["code"]
        h = E.line_hash(code)
        ai_hash = None
        if h in ai_hashes:
            label, ai_hash = "ai_giu_nguyen", h
        else:
            same = ai_by_file.get(_norm(item["file"]), [])
            ratio, match = _best_match(code, same)
            if ratio < SIMILAR and len(all_ai) != len(same):
                r2, m2 = _best_match(code, all_ai, SIMILAR_OTHER_FILE)
                if r2 >= SIMILAR_OTHER_FILE:
                    ratio, match = r2, m2
            if ratio >= SIMILAR:
                label, ai_hash = "ai_da_sua", E.line_hash(match)
            else:
                label = "nguoi_viet"
        row = {"file": item["file"], "line": item["line"], "code": code, "label": label}
        if ai_hash:
            row["ai_hash"] = ai_hash
        out.append(row)
    return out


def summarize(lines):
    stats = {k: 0 for k in LABELS}
    for ln in lines:
        stats[ln["label"]] += 1
    return stats


def attribute_patch(patch, evs, task_id=None, patterns=None):
    """Bản thuần: patch + sự kiện → kết quả mục 0.3 (không có DI; dependence.py điền).
    patterns=None → DEFAULT_IGNORE. Các file bị bỏ qua liệt kê ở "ignored_files"."""
    patterns = ignore_patterns() if patterns is None else patterns
    hashes, by_file = ai_lines_from_events(evs)
    added, ignored = [], set()
    for item in parse_patch(patch):
        if is_ignored(item["file"], patterns):
            ignored.add(item["file"])
        else:
            added.append(item)
    lines = attribute_lines(added, hashes, by_file)
    removed = [r for r in parse_removed(patch) if not is_ignored(r["file"], patterns)]
    return {"task_id": task_id, "lines": lines, "stats": summarize(lines), "ignored_files": sorted(ignored),
            "removed": removed}


# --- phần dùng git -----------------------------------------------------------------
def task_range(repo, evs):
    """(base, head) của task: base_commit trong state.jsonl, hoặc cha của commit đầu tiên của task."""
    state = E.load_state(repo)
    commits = [e.get("commit") for e in evs if e.get("event") == "commit" and e.get("commit")]
    head = commits[-1] if commits else "HEAD"
    base = state.get("base_commit") if state.get("task_id") == (evs[0].get("task_id") if evs else None) else None
    if not base and commits:
        parent = E.git(repo, "rev-parse", commits[0] + "^")
        base = parent.strip() if parent else None
    if not base:
        parent = E.git(repo, "rev-parse", head + "^")
        base = parent.strip() if parent else None
    return base, head


def task_patch(repo, evs):
    base, head = task_range(repo, evs)
    if base:
        return E.git(repo, "diff", "--no-color", "--no-ext-diff", "-U0", base, head) or ""
    # repo mới có đúng 1 commit
    return E.git(repo, "show", "--no-color", "--format=", "-U0", head) or ""


def attribute(repo, task_id=None):
    task_id = task_id or E.current_task_id(repo)
    evs = E.read_events(repo, task_id)
    from .install import load_config
    return attribute_patch(task_patch(repo, evs), evs, task_id, ignore_patterns(load_config(repo)))
