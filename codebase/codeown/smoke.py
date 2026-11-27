"""Bằng chứng đã nối model thật: gọi 1 ca Examiner, 1 Grader, 1 Reflector, in JSON + token.

    python -m codeown.smoke                         # 3 ca, cần .env có MODEL_PROVIDER=anthropic + API_KEY
    python -m codeown.smoke --variance eval/benchmark.csv
        # chạy mọi câu mode grade 2 lần, in tỉ lệ đổi nhãn (Q10: >10% thì chuyển sang chấm đa số 3 lần)
Chạy tay trước lượt eval 1. Có gọi model thật nên tốn tiền.
"""
import csv
import json
import sys

import ai
import tracing

from .examiner import examine
from .grader import grade
from .reflector import reflect

CODE = ["import hmac", "def login(user, pw):",
        "    row = db.execute('SELECT hash FROM users WHERE name=?', (user,))",
        "    if row is None:", "        return False",
        "    return hmac.compare_digest(hash_pw(pw), row[0])"]
LINES = [{"file": "app/auth.py", "line": 10 + i, "code": c, "label": "ai_giu_nguyen"}
         for i, c in enumerate(CODE * 4)]
EVENTS = [{"id": "ev_000001", "event": "prompt", "branch": "feat/login", "prompt": "viết hàm login có hash mật khẩu"}]


def traced(name, fn):
    tracing.begin(name)
    try:
        out = fn()
    finally:
        summary, _ = tracing.end()
    print("== %s · model %s · gọi %d · token vào %d · ra %d" % (
        name, ",".join(summary["models"]), summary["model_calls"], summary["tokens_in"], summary["tokens_out"]))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return out


def smoke():
    exam = traced("examiner", lambda: examine(LINES, di=64, task_intent="nhánh: feat/login", task_id="smoke"))
    q = exam["questions"][0]
    traced("grader", lambda: grade(q, q["rubric_hidden"], "So sánh hash bằng hàm thời gian hằng để kẻ xấu không đo được "
                                                         "thời gian phản hồi mà đoán mật khẩu.", diff_codes=CODE))
    results = [dict(q, label="mot_phan", missing_concept=q["concept"])]
    traced("reflector", lambda: reflect("smoke", EVENTS, LINES, [{k: v for k, v in r.items() if k != "rubric_hidden"}
                                                                for r in results]))


def variance(path):
    with open(path, encoding="utf-8-sig") as f:
        cases = [json.loads(r["input"]) for r in csv.DictReader(f) if '"grade"' in r["input"]]
    changed = 0
    for c in cases:
        q = {"qid": c.get("case_id"), "question": c["question"], "concept": c.get("concept"), "lines": c.get("lines")}
        labels = [grade(q, c["rubric"], c["answer"])["label"] for _ in range(2)]
        changed += labels[0] != labels[1]
        print("%s: %s" % (c.get("case_id"), " / ".join(str(l) for l in labels)))
    print("Đổi nhãn %d/%d câu (%.0f%%)" % (changed, len(cases), 100.0 * changed / max(len(cases), 1)))


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if ai.MODEL_PROVIDER == "fake":
        print("Đang ở chế độ giả: điền MODEL_PROVIDER=anthropic và API_KEY trong .env rồi chạy lại.")
        return 1
    if argv[:1] == ["--variance"]:
        variance(argv[1])
    else:
        smoke()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
