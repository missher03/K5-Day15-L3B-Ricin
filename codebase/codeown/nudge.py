"""Luật nhắc trong lúc code (docs/design.md §5.3). Code tất định, tối đa 1 lần / 15 phút.

  lap_loi      dán cùng lỗi 3 lần liên tiếp
  nhan_nhieu_dong     nhận ≥50 dòng AI trong <30 giây sau một prompt
  lam_ho_ca_tinh_nang   prompt lam_ho cho cả một tính năng
  di_cao         DI vượt 70

Mỗi lần nhắc kèm số đo cụ thể (nguyên tắc "cho thấy hệ thống làm gì, vì sao"). Người dùng bỏ qua được.
"""
import difflib
import re

from . import events as E

COOLDOWN_SEC = 15 * 60
SAME_ERROR_N = 3
BULK_LINES = 50
BULK_WINDOW_SEC = 30
DI_HIGH = 70
_WHOLE = re.compile(
    r"(?i)toàn bộ|cả (?:app|ứng dụng|trang|tính năng|chức năng|module|hệ thống|project|dự án)|"
    r"(?:một|1) (?:tính năng|chức năng|module) (?:hoàn chỉnh|đầy đủ)|từ đầu đến cuối|end[- ]to[- ]end|"
    r"\bwhole\b|\bentire\b|\bfull (?:app|feature|crud|module|page)\b|\bcomplete (?:app|feature)\b|"
    r"\bfrom scratch\b|làm hết|viết hết")


def _last_nudge_ts(evs):
    for ev in reversed(evs):
        if ev.get("event") == "nudge":
            return E.parse_ts(ev.get("ts"))
    return None


def rule_lap_loi(evs, labels):
    prompts = [e for e in evs if e.get("event") == "prompt"][-SAME_ERROR_N:]
    if len(prompts) < SAME_ERROR_N:
        return None
    if any(labels.get(p.get("id")) not in ("debug_dan_loi", "debug_co_gia_thuyet") for p in prompts):
        return None
    texts = [re.sub(r"\s+", " ", p.get("prompt") or "").lower() for p in prompts]
    if all(difflib.SequenceMatcher(None, texts[0], t).ratio() >= 0.8 for t in texts[1:]):
        return {"rule": "lap_loi", "metric": {"times": SAME_ERROR_N},
                "message": "Bạn đã dán cùng một lỗi %d lần liên tiếp. Thử đọc dòng lỗi đầu tiên và "
                           "đoán nguyên nhân trước khi hỏi tiếp?" % SAME_ERROR_N}
    return None


def rule_nhan_nhieu_dong(evs):
    last_prompt = None
    total = 0
    for ev in evs:
        if ev.get("event") == "prompt":
            last_prompt, total = E.parse_ts(ev.get("ts")), 0
        elif ev.get("event") == "ai_edit" and last_prompt is not None:
            t = E.parse_ts(ev.get("ts"))
            if t and (t - last_prompt).total_seconds() <= BULK_WINDOW_SEC:
                total += len(ev.get("line_hashes") or [])
    if total >= BULK_LINES:
        return {"rule": "nhan_nhieu_dong", "metric": {"lines": total, "seconds": BULK_WINDOW_SEC},
                "message": "Vừa nhận %d dòng code trong chưa tới %d giây. Đọc qua phần xử lý lỗi "
                           "trước khi chạy?" % (total, BULK_WINDOW_SEC)}
    return None


def rule_lam_ho_ca_tinh_nang(evs, labels):
    prompts = [e for e in evs if e.get("event") == "prompt"]
    if not prompts:
        return None
    p = prompts[-1]
    if labels.get(p.get("id")) == "lam_ho" and _WHOLE.search(p.get("prompt") or ""):
        return {"rule": "lam_ho_ca_tinh_nang", "metric": {"prompt_id": p.get("id")},
                "message": "Bạn vừa nhờ viết cả một tính năng. Muốn tự viết phần lõi và để công cụ "
                           "làm phần lặp lại không?"}
    return None


def rule_di_cao(di, feats):
    if di is not None and di > DI_HIGH:
        kept = feats.get("f1", 0)
        return {"rule": "di_cao", "metric": {"di": di, "f1": kept},
                "message": "DI của task này là %d (%.0f%% code AI bạn nhận không sửa). "
                           "Sau commit, CodeOwn sẽ hỏi bạn vài câu về phần này." % (di, 100 * kept)}
    return None


def check_nudge(evs, di=None, feats=None, now=None):
    """Trả lời nhắc đầu tiên khớp luật (dict) hoặc None. Tôn trọng thời gian chờ 15 phút."""
    feats = feats or {}
    now = now or E.parse_ts(E.now_iso())
    last = _last_nudge_ts(evs)
    if last and now and (now - last).total_seconds() < COOLDOWN_SEC:
        return None
    labels = feats.get("prompt_labels") or {}
    for res in (rule_lap_loi(evs, labels), rule_nhan_nhieu_dong(evs),
                rule_lam_ho_ca_tinh_nang(evs, labels), rule_di_cao(di, feats)):
        if res:
            return res
    return None
