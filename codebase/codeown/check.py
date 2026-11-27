"""Lệnh của B (hợp đồng 0.6): `check start`, `check answer`, `reflect`, `ledger save`.

Giữ kết quả phiên ở `.codeown/check/<task_id>.json` (có rubric ẩn); stdout không bao giờ có `rubric_hidden`.
Chạy: `python -m codeown check start --task <id> [--from attribution.json]` (`__main__.py` của A chuyển
`check` / `reflect` / `ledger` sang `main(argv)` sau khi chdir về gốc repo, nên `.codeown/` là của repo).
"""
import argparse
import json
import os
import sys

from . import ledger
from .examiner import examine
from .grader import grade
from .reflector import reflect

CHECK_DIR = os.path.join(".codeown", "check")
EVENTS = os.path.join(".codeown", "events.jsonl")


class CheckError(RuntimeError):
    pass


def _session_path(task_id):
    return os.path.join(CHECK_DIR, "%s.json" % task_id)


def load_session(task_id):
    try:
        with open(_session_path(task_id), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise CheckError("chưa có Check cho task %s — chạy `check start` trước" % task_id)


def _write_session(session):
    os.makedirs(CHECK_DIR, exist_ok=True)
    with open(_session_path(session["task_id"]), "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=1)


def public(questions):
    return [{k: v for k, v in q.items() if k != "rubric_hidden"} for q in questions]


def load_events(task_id, path=EVENTS):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [e for e in (json.loads(l) for l in f if l.strip()) if e.get("task_id") == task_id]


def task_intent(events):
    """Mục đích task gom bằng code: tên nhánh + 3 prompt đầu; không có thì None ("chưa rõ")."""
    branch = next((e["branch"] for e in events if e.get("branch")), None)
    prompts = [e["prompt"] for e in events if e.get("event") == "prompt" and e.get("prompt")][:3]
    parts = (["nhánh: " + branch] if branch else []) + ["prompt: " + p for p in prompts]
    return "; ".join(parts) or None


def _attribution(task_id, source):
    if source:
        with open(source, encoding="utf-8") as f:
            return json.load(f)
    from .events import find_repo
    from .monitor import attribution_report  # phần của A: dòng 0.3 + DI
    return attribution_report(find_repo(), task_id)


def start(task_id, source=None):
    attr = _attribution(task_id, source)
    result = examine(attr["lines"], attr.get("di", 0), task_intent(load_events(task_id)),
                     dont_ask=ledger.recent_understood(), ask_first=ledger.weak_concepts(), task_id=task_id,
                     removed=attr.get("removed", ()))
    if "skip" in result:
        return {"skip": result["skip"]}
    _write_session({"task_id": task_id, "questions": result["questions"],
                    "lines": attr["lines"], "answers": {}})
    return dict(result, questions=public(result["questions"]))


def answer(task_id, qid, text):
    session = load_session(task_id)
    q = next((q for q in session["questions"] if q["qid"] == qid), None)
    if q is None:
        raise CheckError("không có câu %s trong task %s" % (qid, task_id))
    history = session["answers"].setdefault(qid, [])
    if history and history[-1]["result"]["final"]:
        raise CheckError("câu %s đã chấm xong" % qid)
    # Vòng chỉ tăng khi câu trả lời được chấm; trả lời lại sau gợi ý mức 1 không tốn vòng.
    rnd = 1 + sum(1 for h in history if h["result"]["status"] == "graded")
    result = grade(q, q["rubric_hidden"], text, round=rnd, diff_codes=[l["code"] for l in session["lines"]])
    # shortcut: chưa kèm gợi ý docs khi dừng ở vòng 2 (chưa có search_docs trong tools.py); thêm khi C có docs offline.
    history.append({"answer": text, "result": result})
    _write_session(session)
    return result


def check_results(session):
    """Kết quả từng câu (không có rubric): nhãn và khái niệm hổng của lần chấm cuối, None nếu chưa chấm."""
    out = []
    for q in session["questions"]:
        graded = [h["result"] for h in session["answers"].get(q["qid"], []) if h["result"]["status"] == "graded"]
        last = graded[-1] if graded else {}
        out.append(dict({k: q[k] for k in ("qid", "file", "lines", "concept", "question")},
                        label=last.get("label"), missing_concept=last.get("missing_concept")))
    return out


def run_reflect(task_id):
    session = load_session(task_id)
    return reflect(task_id, load_events(task_id), session["lines"], check_results(session))


def save(task_id):
    """Chỉ gọi khi người dùng bấm Lưu (ADR 0003)."""
    items = [r for r in check_results(load_session(task_id)) if r["label"]]
    return {"ok": True, "saved": ledger.save(task_id, items)}


def main(argv=None):
    p = argparse.ArgumentParser(prog="codeown")
    sub = p.add_subparsers(dest="group", required=True)
    check = sub.add_parser("check").add_subparsers(dest="cmd", required=True)
    s = check.add_parser("start")
    s.add_argument("--task", required=True)
    s.add_argument("--from", dest="source", help="file JSON kết quả gán dòng 0.3 (khi chưa có attribution của A)")
    s.add_argument("--json", action="store_true")
    a = check.add_parser("answer")
    a.add_argument("--task", required=True)
    a.add_argument("--qid", required=True)
    a.add_argument("--text", required=True)
    a.add_argument("--json", action="store_true")
    r = sub.add_parser("reflect")
    r.add_argument("--task", required=True)
    r.add_argument("--json", action="store_true")
    led = sub.add_parser("ledger").add_subparsers(dest="cmd", required=True)
    ls = led.add_parser("save")
    ls.add_argument("--task", required=True)
    # Extension gửi kèm markdown Reflect qua stdin; Sổ lấy khái niệm từ kết quả Check (ADR 0003) nên chỉ đọc cho hết.
    ls.add_argument("--from-stdin", action="store_true")
    ls.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if getattr(args, "from_stdin", False):
        sys.stdin.read()

    sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252
    try:
        if args.group == "check" and args.cmd == "start":
            out = start(args.task, args.source)
        elif args.group == "check":
            out = answer(args.task, args.qid, args.text)
        elif args.group == "reflect":
            out = run_reflect(args.task)
        else:
            out = save(args.task)
    except Exception as e:  # mọi lỗi thành {"error"} + mã thoát ≠ 0 (hợp đồng 0.6)
        print(json.dumps({"error": "%s: %s" % (type(e).__name__, e)}, ensure_ascii=False))
        return 1
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
