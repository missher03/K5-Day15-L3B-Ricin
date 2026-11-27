"""Luồng chính của bản chạy thử. `python run.py`, `run.py eval`, `run.py simulate` đều gọi answer(text).

Hợp đồng của khung: answer(text: str) -> {"output": str}.
Ô input của câu thử là MỘT chuỗi JSON có "mode" (task.md mục 0.7):
  {"mode": "monitor", "session_id": "demo01"}                 ← phần A
  {"mode": "monitor", "events": [...], "patch": "..."}       ← phần A, dữ liệu nằm ngay trong câu thử
  {"mode": "examine", "diff_id": "demo01"}                    ← phần B: câu hỏi + rubric ẩn (eval cần rubric để chấm)
  {"mode": "grade", "case_id", "question", "rubric", "answer", "round"?, "diff"?}  ← phần B: kết quả chấm 0.5
Input không phải JSON hoặc mode lạ → từ chối (spec.md §5). Output là chuỗi JSON để run_eval.py và người chấm đọc.
Agent không đọc truth.json (đáp án của bộ câu thử): dòng + DI lấy từ lõi gán dòng của A.

Hình dạng: workflow cố định (spec.md §4). Người giữ file: C; mỗi nhánh mode do người làm phần đó điền.
"""
import json

from tracing import note
from tools import load_session

REFUSAL = ("CodeOwn chỉ hỏi và chấm để bạn tự hiểu code của mình, không viết code hay đưa đáp án. "
           'Gửi JSON có trường mode (monitor / examine / grade), ví dụ {"mode": "monitor", "session_id": "demo01"}.')


def _dump(obj):
    return json.dumps(obj, ensure_ascii=False)


def _analyze(req, session_id):
    from codeown.monitor import analyze_offline
    from codeown.events import parse_ts
    if req.get("events") is not None:
        evs, patch = req["events"], req.get("patch")
    else:
        sess = load_session(session_id or "")
        evs, patch = sess["events"], sess.get("patch")
    now = parse_ts(req["now"]) if req.get("now") else (parse_ts(evs[-1]["ts"]) if evs else None)
    return evs, analyze_offline(evs, patch, task_id=session_id, mode="rules", now=now)


def _monitor(req):
    _, res = _analyze(req, req.get("session_id"))
    res.pop("lines", None)  # bỏ cho gọn; muốn xem từng dòng thì gọi codeown attribute
    note("monitor: di=%s nudge=%s" % (res["di"], (res["pending_nudge"] or {}).get("rule")))
    return res


def _examine(req):
    from codeown.examiner import examine
    diff_id = req.get("diff_id")
    _, res = _analyze(req, diff_id)
    return examine(res["lines"], res["di"], req.get("task_intent"), task_id=diff_id)


def _grade(req):
    from codeown.grader import grade
    question = {"qid": req.get("case_id"), "question": req["question"], "concept": req.get("concept"),
                "lines": req.get("lines")}
    return grade(question, req["rubric"], req["answer"], round=req.get("round", 1), diff_codes=req.get("diff", []))


MODES = {"monitor": _monitor, "examine": _examine, "grade": _grade}


def answer(text: str) -> dict:
    try:
        req = json.loads(text)
    except (TypeError, ValueError):
        req = None
    if not isinstance(req, dict) or req.get("mode") not in MODES:
        note("từ chối: input không phải yêu cầu JSON có mode hợp lệ")
        return {"output": _dump({"refused": True, "message": REFUSAL})}
    try:
        return {"output": _dump(MODES[req["mode"]](req))}
    except Exception as exc:  # noqa: BLE001 — lỗi một câu không làm sập cả lượt
        return {"output": _dump({"error": "%s: %s" % (type(exc).__name__, exc)})}
