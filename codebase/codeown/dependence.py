"""Chỉ số phụ thuộc DI (docs/design.md §5.1). Toàn bộ là code tất định, không gọi AI ngoài Classifier.

  f1 = ai_giu_nguyen / (ai_giu_nguyen + ai_da_sua)            — nhận code AI mà không sửa
  f2 = tỉ lệ prompt lam_ho + debug_dan_loi trên mọi prompt      — giao việc / dán lỗi
  f3 = số chuỗi ≥2 prompt liền nhau có cùng dòng lỗi (dòng "...Error/Exception..." đầu tiên, giống ≥0,8);
       commit / đánh dấu tay ở giữa thì cắt chuỗi
  f4 = trung vị số giây từ lúc AI ghi một dòng (ai_edit đầu tiên có dòng đó) tới commit kế tiếp,
       tính trên các dòng AI có trong diff (giữ nguyên hoặc đã sửa)  — commit vội
  f5 = 1 nếu có dòng nguoi_viet trong file test

  DI = 100 × (0,3·f1 + 0,25·f2 + 0,2·f3ₙ + 0,15·(1−f4ₙ) + 0,1·(1−f5))
  f3ₙ = min(f3, F3_CAP)/F3_CAP · f4ₙ = min(f4, F4_CAP)/F4_CAP

Trọng số và mức chặn là giả định ban đầu, chốt cùng chuẩn "đạt" ở CP2 rồi không đổi.
Không đo được f4 (chưa commit / không có dòng AI) thì f4 = F4_CAP, tức không cộng điểm phụ thuộc, và ghi vào "missing".
Định nghĩa khớp bộ sinh mẫu của C (data/samples/build_samples.py) để eval so được.
"""
import difflib
import re
import statistics

from . import events as E
from .classifier import classify

WEIGHTS = {"f1": 0.30, "f2": 0.25, "f3": 0.20, "f4": 0.15, "f5": 0.10}
F3_CAP = 5
F4_CAP = 600  # giây
SAME_ERROR = 0.8
_TEST_FILE = re.compile(r"(?i)(^|/)(tests?|__tests__|spec)(/|$)|(^|/)test_[^/]*$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$")


def is_test_file(path):
    return bool(_TEST_FILE.search((path or "").replace("\\", "/")))


def label_prompts(evs, mode=None):
    """Nhãn cho mọi sự kiện prompt. Dùng nhãn đã lưu ở meta.label nếu có (không gọi lại model)."""
    out = {}
    for ev in evs:
        if ev.get("event") == "prompt":
            lab = (ev.get("meta") or {}).get("label")
            out[ev.get("id")] = lab or classify(ev.get("prompt") or "", mode)
    return out


_ERR_SIG = re.compile(r"[A-Za-z_.]*(?:Error|Exception)\b[^\n]*")


def error_signature(prompt):
    """Dòng lỗi đầu tiên trong prompt ("KeyError: 'id'"…), hoặc None."""
    m = _ERR_SIG.search(prompt or "")
    return m.group(0).strip() if m else None


def same_error(a, b):
    return bool(a and b) and difflib.SequenceMatcher(None, a, b).ratio() >= SAME_ERROR


def error_runs(evs):
    """Các chuỗi prompt liền nhau cùng lỗi → [(độ dài, sự kiện prompt cuối)]. commit / manual_mark cắt chuỗi."""
    runs, run, prev, last = [], 0, None, None
    for ev in evs:
        kind = ev.get("event")
        if kind in ("commit", "manual_mark"):
            if run:
                runs.append((run, last))
            run, prev = 0, None
            continue
        if kind != "prompt":
            continue
        sig = error_signature(ev.get("prompt"))
        if prev is not None and same_error(prev, sig):
            run += 1
        else:
            if run:
                runs.append((run, last))
            run = 1
        prev, last = sig, ev
    if run:
        runs.append((run, last))
    return runs


def repeated_error_chains(evs, labels=None):
    """f3: số chuỗi ≥2 prompt liền nhau cùng lỗi."""
    return sum(1 for n, _ in error_runs(evs) if n >= 2)


def line_waits(evs, lines):
    """Số giây từ lúc AI ghi mỗi dòng AI trong diff tới commit kế tiếp sau đó."""
    first_edit, commits = {}, []
    for ev in evs:
        t = E.parse_ts(ev.get("ts"))
        if t is None:
            continue
        if ev.get("event") == "ai_edit":
            for h in ev.get("line_hashes") or []:
                first_edit.setdefault(h, t)
        elif ev.get("event") == "commit":
            commits.append(t)
    out = []
    for ln in lines or []:
        t0 = first_edit.get(ln.get("ai_hash"))
        if ln.get("label") == "nguoi_viet" or t0 is None:
            continue
        after = [c for c in commits if c >= t0]
        if after:
            out.append((after[0] - t0).total_seconds())
    return out


def features(evs, attribution=None, mode=None):
    stats = (attribution or {}).get("stats") or {}
    lines = (attribution or {}).get("lines") or []
    missing = []

    kept, edited = stats.get("ai_giu_nguyen", 0), stats.get("ai_da_sua", 0)
    f1 = kept / (kept + edited) if kept + edited else 0.0
    if not kept + edited:
        missing.append("f1")

    labels = label_prompts(evs, mode)
    f2 = (sum(1 for v in labels.values() if v in ("lam_ho", "debug_dan_loi")) / len(labels)) if labels else 0.0
    if not labels:
        missing.append("f2")

    f3 = repeated_error_chains(evs)

    secs = line_waits(evs, lines)
    f4 = statistics.median(secs) if secs else None
    if f4 is None:
        missing.append("f4")

    f5 = 1 if any(ln["label"] == "nguoi_viet" and is_test_file(ln["file"]) for ln in lines) else 0

    return {"f1": round(f1, 3), "f2": round(f2, 3), "f3": f3,
            "f4_sec": None if f4 is None else round(f4, 1), "f5": f5,
            "missing": missing, "prompt_labels": labels}


def di_from_features(f):
    f3n = min(f["f3"], F3_CAP) / F3_CAP
    f4n = 1.0 if f["f4_sec"] is None else min(f["f4_sec"], F4_CAP) / F4_CAP
    score = (WEIGHTS["f1"] * f["f1"] + WEIGHTS["f2"] * f["f2"] + WEIGHTS["f3"] * f3n
             + WEIGHTS["f4"] * (1 - f4n) + WEIGHTS["f5"] * (1 - f["f5"]))
    return int(round(100 * score))


def compute(evs, attribution=None, mode=None):
    """→ {"di", "features"}. Không có sự kiện nào → di = None."""
    if not evs:
        return {"di": None, "features": {}}
    f = features(evs, attribution, mode)
    return {"di": di_from_features(f), "features": f}

