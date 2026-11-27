"""Chỉ số phụ thuộc DI (docs/design.md §5.1). Toàn bộ là code tất định, không gọi AI ngoài Classifier.

  f1 = ai_giu_nguyen / (ai_giu_nguyen + ai_da_sua)            — nhận code AI mà không sửa
  f2 = tỉ lệ prompt lam_ho + debug_dan_loi trong các prompt về code (bỏ nhãn khac: chào hỏi, cảm ơn…)
  f3 = số chuỗi ≥2 prompt liền nhau chứa cùng lỗi (giống ≥0,8), không có dòng tự viết xen giữa
  f4 = trung vị số giây từ ai_edit tới commit kế tiếp          — commit vội
  f5 = 1 nếu có dòng nguoi_viet trong file test

  DI = 100 × (0,3·f1 + 0,25·f2 + 0,2·f3ₙ + 0,15·(1−f4ₙ) + 0,1·(1−f5))
  f3ₙ = min(f3, F3_CAP)/F3_CAP · f4ₙ = min(f4, F4_CAP)/F4_CAP

Trọng số và mức chặn là giả định ban đầu, chốt cùng chuẩn "đạt" ở CP2 rồi không đổi.
Thiếu dữ liệu cho f4 (chưa commit) thì f4ₙ = 0,5 (trung tính) và ghi vào "missing".
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


def _error_text(prompt):
    return re.sub(r"\s+", " ", (prompt or "")).strip().lower()[:600]


def repeated_error_chains(evs, labels):
    """f3: đếm chuỗi ≥2 prompt debug liền nhau mà cùng lỗi. commit / manual_mark / sửa tay cắt chuỗi."""
    chains, run, prev = 0, 0, None
    for ev in evs:
        kind = ev.get("event")
        if kind in ("commit", "manual_mark"):
            run, prev = 0, None
            continue
        if kind != "prompt":
            continue
        lab = labels.get(ev.get("id"))
        if lab not in ("debug_dan_loi", "debug_co_gia_thuyet"):
            run, prev = 0, None
            continue
        cur = _error_text(ev.get("prompt"))
        if prev is not None and difflib.SequenceMatcher(None, prev, cur).ratio() >= SAME_ERROR:
            run += 1
            if run == 2:
                chains += 1
        else:
            run = 1
        prev = cur
    return chains


def edit_to_commit_seconds(evs):
    """Danh sách số giây từ mỗi ai_edit tới commit kế tiếp sau nó."""
    out, pending = [], []
    for ev in evs:
        kind = ev.get("event")
        if kind == "ai_edit":
            t = E.parse_ts(ev.get("ts"))
            if t:
                pending.append(t)
        elif kind == "commit":
            t = E.parse_ts(ev.get("ts"))
            if t:
                out.extend(max(0.0, (t - p).total_seconds()) for p in pending)
            pending = []
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
    coding = [v for v in labels.values() if v != "khac"]
    f2 = (sum(1 for v in coding if v in ("lam_ho", "debug_dan_loi")) / len(coding)) if coding else 0.0
    if not coding:
        missing.append("f2")

    f3 = repeated_error_chains(evs, labels)

    secs = edit_to_commit_seconds(evs)
    f4 = statistics.median(secs) if secs else None
    if f4 is None:
        missing.append("f4")

    f5 = 1 if any(ln["label"] == "nguoi_viet" and is_test_file(ln["file"]) for ln in lines) else 0

    return {"f1": round(f1, 3), "f2": round(f2, 3), "f3": f3,
            "f4_sec": None if f4 is None else round(f4, 1), "f5": f5,
            "missing": missing, "prompt_labels": labels}


def di_from_features(f):
    f3n = min(f["f3"], F3_CAP) / F3_CAP
    f4n = 0.5 if f["f4_sec"] is None else min(f["f4_sec"], F4_CAP) / F4_CAP
    score = (WEIGHTS["f1"] * f["f1"] + WEIGHTS["f2"] * f["f2"] + WEIGHTS["f3"] * f3n
             + WEIGHTS["f4"] * (1 - f4n) + WEIGHTS["f5"] * (1 - f["f5"]))
    return int(round(100 * score))


def compute(evs, attribution=None, mode=None):
    """→ {"di", "features"}. Không có sự kiện nào → di = None."""
    if not evs:
        return {"di": None, "features": {}}
    f = features(evs, attribution, mode)
    return {"di": di_from_features(f), "features": f}

