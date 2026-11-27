"""Luật nhắc trong lúc code (docs/design.md §5.3). Code tất định, tối đa 1 lần / 15 phút.

Luật (tên khớp bộ câu thử của C):
  lap_loi              dán cùng một lỗi ≥3 prompt liên tiếp
  nhan_nhieu_dong      AI ghi ≥50 dòng trong vòng 30 giây
  lam_ho_ca_tinh_nang  prompt nhờ làm cả một tính năng ("toàn bộ tính năng…", "code hết chức năng…")
  di_cao               DI vượt 70

Mỗi luật được xét trên CẢ phiên (scan_triggers), không chỉ lúc cuối: mỗi lần kích hoạt có thời điểm riêng.
Mỗi lần nhắc kèm số đo cụ thể (nguyên tắc "cho thấy hệ thống làm gì, vì sao"). Người dùng bỏ qua được.
"""
import re

from . import events as E
from .dependence import error_runs

COOLDOWN_SEC = 15 * 60
SAME_ERROR_N = 3
BULK_LINES = 50
BULK_WINDOW_SEC = 30
DI_HIGH = 70
_WHOLE = re.compile(
    r"(?i)toàn bộ|(?:làm|code|viết) hết (?:tính năng|chức năng|phần|module|trang|app)|"
    r"cả (?:app|ứng dụng|trang|tính năng|chức năng|module|hệ thống|project|dự án)|"
    r"(?:một|1) (?:tính năng|chức năng|module) (?:hoàn chỉnh|đầy đủ)|từ đầu đến cuối|end[- ]to[- ]end|"
    r"\bwhole\b|\bentire\b|\bfull (?:app|feature|crud|module|page)\b|\bcomplete (?:app|feature)\b|"
    r"\bfrom scratch\b")

MESSAGES = {
    "lap_loi": "Bạn đã dán cùng một lỗi %(times)d lần liên tiếp. Thử đọc dòng lỗi đầu tiên và đoán nguyên nhân "
               "trước khi hỏi tiếp?",
    "nhan_nhieu_dong": "Vừa nhận %(lines)d dòng code trong chưa tới %(seconds)d giây. Đọc qua phần xử lý lỗi "
                       "trước khi chạy?",
    "lam_ho_ca_tinh_nang": "Bạn vừa nhờ viết cả một tính năng. Muốn tự viết phần lõi và để công cụ làm phần "
                           "lặp lại không?",
    "di_cao": "DI của task này là %(di)d (%(pct).0f%% code AI bạn nhận không sửa). Sau commit, CodeOwn sẽ hỏi "
              "bạn vài câu về phần này.",
}


_FEATURE_ASK = re.compile(
    r"(?i)\b(?:làm|thêm|viết|code|tạo|build|implement|add)\b(?:\s+(?:giúp|cho|hộ)\s+(?:mình|tôi|em))?\s+"
    r"(?:\w+\s+)?(?:chức năng|tính năng|API|middleware|module|endpoint|feature)\b")


def is_whole_feature(prompt, label=None):
    """Nhờ làm cả một tính năng: nói thẳng ("toàn bộ…", "code hết chức năng…"), hoặc prompt nhờ làm hộ
    (nhãn lam_ho) mà đối tượng là cả một chức năng / API / middleware chứ không phải một hàm, một lỗi."""
    p = prompt or ""
    return bool(_WHOLE.search(p)) or (label == "lam_ho" and bool(_FEATURE_ASK.search(p)))


def _trigger(rule, ev_or_ts, metric):
    ts = ev_or_ts if isinstance(ev_or_ts, str) else (ev_or_ts or {}).get("ts")
    ev_id = None if isinstance(ev_or_ts, str) else (ev_or_ts or {}).get("id")
    return {"rule": rule, "ts": ts, "event_id": ev_id, "metric": metric, "message": MESSAGES[rule] % metric}


def scan_triggers(evs, di=None, feats=None, now_ts=None):
    """Mọi lần luật kích hoạt trong phiên, theo thời gian."""
    feats = feats or {}
    out = []
    for n, last in error_runs(evs):
        if n >= SAME_ERROR_N:
            out.append(_trigger("lap_loi", last, {"times": n}))
    edits = [(E.parse_ts(e.get("ts")), e) for e in evs if e.get("event") == "ai_edit"]
    edits = [(t, e) for t, e in edits if t is not None]
    for t0, _ in edits:
        window = [(t, e) for t, e in edits if 0 <= (t - t0).total_seconds() < BULK_WINDOW_SEC]
        total = sum(len(e.get("line_hashes") or []) for _, e in window)
        if total >= BULK_LINES:
            out.append(_trigger("nhan_nhieu_dong", window[-1][1], {"lines": total, "seconds": BULK_WINDOW_SEC}))
            break
    labels = feats.get("prompt_labels") or {}
    for e in evs:
        if e.get("event") == "prompt" and is_whole_feature(e.get("prompt"), labels.get(e.get("id"))):
            out.append(_trigger("lam_ho_ca_tinh_nang", e, {"prompt_id": e.get("id")}))
            break
    if di is not None and di > DI_HIGH:
        commits = [e for e in evs if e.get("event") == "commit"]
        anchor = commits[-1] if commits else (now_ts or E.now_iso())
        out.append(_trigger("di_cao", anchor, {"di": di, "pct": 100 * feats.get("f1", 0), "f1": feats.get("f1", 0)}))
    out.sort(key=lambda x: E.parse_ts(x["ts"]) or E.parse_ts(E.now_iso()))
    return out


def fired(triggers, last=None):
    """Áp 15 phút chờ theo thứ tự thời gian → các lần nhắc thật sự hiện (bắt đầu sau lần nhắc `last`)."""
    out = []
    for tr in triggers:
        t = E.parse_ts(tr["ts"])
        if t is None:
            continue
        if last is not None and t <= last:
            continue
        if out and (t - E.parse_ts(out[-1]["ts"])).total_seconds() < COOLDOWN_SEC:
            continue
        if last is not None and (t - last).total_seconds() < COOLDOWN_SEC:
            continue
        out.append(tr)
    return out


def _last_nudge_ts(evs):
    for ev in reversed(evs):
        if ev.get("event") == "nudge":
            return E.parse_ts(ev.get("ts"))
    return None


def check_nudge(evs, di=None, feats=None, now=None):
    """Lời nhắc nên hiện lúc này (dict: rule, message, metric, ts) hoặc None.
    Chỉ xét các lần kích hoạt sau lần nhắc gần nhất, và tôn trọng 15 phút chờ."""
    now = now or E.parse_ts(E.now_iso())
    last = _last_nudge_ts(evs)
    if last and now and (now - last).total_seconds() < COOLDOWN_SEC:
        return None
    now_ts = now.isoformat(timespec="seconds") if now else None
    pending = fired(scan_triggers(evs, di, feats, now_ts), last)
    return pending[-1] if pending else None
