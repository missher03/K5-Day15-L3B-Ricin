"""Luồng chính của bản chạy thử. `python run.py`, `run.py eval`, `run.py simulate` đều gọi answer(text).

Hợp đồng của khung: answer(text: str) -> {"output": str}.
Ô input của câu thử là MỘT chuỗi JSON có "mode" (task.md mục 0.7):
  {"mode": "monitor", "session_id": "demo01"}                 ← phần A (đã làm)
  {"mode": "monitor", "events": [...], "patch": "..."}       ← phần A, dữ liệu nằm ngay trong câu thử
  {"mode": "examine", "diff_id": "..."}                       ← phần B (chưa làm → kết quả giả, "fake": true)
  {"mode": "grade", ...} · {"mode": "reflect", ...}           ← phần B
Input không phải JSON (vd gõ tay ở `python run.py`) → trả hướng dẫn.
Output là chuỗi JSON để run_eval.py và người chấm đọc được.

Hình dạng: workflow cố định (spec.md §4). Người giữ file: C; mỗi nhánh mode do người làm phần đó điền.
"""
import json
import os

from tracing import note
from tools import load_session

FAKE_MODES = ("examine", "grade", "reflect")


def _dump(obj):
    return json.dumps(obj, ensure_ascii=False)


def _monitor(req):
    from codeown.monitor import analyze_offline
    from codeown.events import parse_ts
    if req.get("events") is not None:
        evs, patch = req["events"], req.get("patch")
    else:
        sess = load_session(req.get("session_id") or "")
        evs, patch = sess["events"], sess.get("patch")
    now = parse_ts(req["now"]) if req.get("now") else (parse_ts(evs[-1]["ts"]) if evs else None)
    res = analyze_offline(evs, patch, task_id=req.get("session_id"), mode="rules", now=now)
    res.pop("lines", None)  # bỏ cho gọn; muốn xem từng dòng thì gọi codeown attribute
    note("monitor: di=%s nudge=%s" % (res["di"], (res["pending_nudge"] or {}).get("rule")))
    return res


def answer(text: str) -> dict:
    try:
        req = json.loads(text)
    except (TypeError, ValueError):
        req = None
    if not isinstance(req, dict) or "mode" not in req:
        return {"output": "CodeOwn nhận một JSON có trường mode (monitor / examine / grade / reflect). "
                          'Ví dụ: {"mode": "monitor", "session_id": "demo01"}'}
    mode = req["mode"]
    try:
        if mode == "monitor":
            return {"output": _dump(_monitor(req))}
        if mode in FAKE_MODES:
            note("dừng: nhánh %s chưa làm, trả kết quả giả" % mode)
            return {"output": _dump({"fake": True, "mode": mode, "note": "phần B chưa nối"})}
    except Exception as exc:  # noqa: BLE001 — lỗi một câu không làm sập cả lượt
        return {"output": _dump({"error": "%s: %s" % (type(exc).__name__, exc)})}
    return {"output": _dump({"error": "mode không hợp lệ: %s" % mode})}
