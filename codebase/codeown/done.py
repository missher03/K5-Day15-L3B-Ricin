"""`codeown done`: chạy cả luồng Check → Reflect → Lưu trong terminal (bản demo dự phòng khi extension trễ).

Chạy: `python -m codeown.done --task <id> [--from attribution.json]`. Khi CLI của A có trên main,
A nối lệnh `done` vào `__main__.py` bằng `done.main(argv)`.
"""
import argparse
import sys

from . import check


def _show_code(session, q):
    start, end = q["lines"]
    for l in session["lines"]:
        if l["file"] == q["file"] and start <= l["line"] <= end:
            print("    %4d | %s" % (l["line"], l["code"]))


def _feedback(r):
    if r["status"] == "need_retry":
        return "Gợi ý: %s" % r["hint"]
    if r["status"] == "need_own_words":
        return r["hint"]
    text = {"hieu": "Bạn hiểu đoạn này.", "mot_phan": "Hiểu một phần.", "chua_hieu": "Chưa hiểu."}[r["label"]]
    if r["missing_concept"]:
        text += " Khái niệm cần xem lại: %s." % r["missing_concept"]
    if r["hint"]:
        text += "\nGợi ý: %s" % r["hint"]
    if r["follow_up"]:
        text += "\nCâu hỏi tiếp: %s" % r["follow_up"]
    return text


def run(task_id, source=None, ask=input):
    started = check.start(task_id, source)
    if "skip" in started:
        print("Không mở Check: %s" % started["skip"])
        return 0
    session = check.load_session(task_id)
    print("CodeOwn: %d câu hỏi về code bạn vừa commit. Bỏ trống để bỏ qua một câu.\n" % len(started["questions"]))
    for q in started["questions"]:
        print("[%s] %s:%d-%d · %s" % (q["qid"], q["file"], q["lines"][0], q["lines"][1], q["question"]))
        _show_code(session, q)
        while True:
            text = ask("> ").strip()
            if not text:
                print("(bỏ qua)\n")
                break
            r = check.answer(task_id, q["qid"], text)
            print(_feedback(r) + "\n")
            if r["final"]:
                break
    report = check.run_reflect(task_id)
    print(report["markdown"])
    if ask("Lưu vào Sổ kiến thức? (y/N) ").strip().lower() == "y":
        print("Đã lưu %d khái niệm." % check.save(task_id)["saved"])
    else:
        print("Không lưu.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="codeown done")
    p.add_argument("--task", required=True)
    p.add_argument("--from", dest="source", help="file JSON kết quả gán dòng 0.3 (khi chưa có attribution của A)")
    args = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        return run(args.task, args.source)
    except (check.CheckError, OSError) as e:
        print("Lỗi: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
