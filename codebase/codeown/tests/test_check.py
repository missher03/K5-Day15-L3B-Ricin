import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

from codeown import check, ledger, llm

LINES = [{"file": "app/auth.py", "line": 40 + i, "code": "if hmac.compare_digest(a, b): pass", "label": "ai_giu_nguyen"}
         for i in range(25)]
QUESTIONS = {"questions": [{"file": "app/auth.py", "lines": [40, 45], "concept": "so sánh thời gian hằng",
                            "question": "Vì sao dùng compare_digest?", "rubric_hidden": "BÍ_MẬT thời gian hằng"}]}
PARTIAL = {"label": "mot_phan", "confidence": 0.8, "missing_concept": "timing attack",
           "hint": "Nghĩ về thời gian phản hồi.", "follow_up": "Kẻ tấn công đo được gì?"}


def model_replies(*payloads):
    replies = iter(payloads)
    return mock.patch.object(llm, "call_model", side_effect=lambda *a, **k: {
        "text": json.dumps(next(replies), ensure_ascii=False), "model": "m", "tokens_in": 1, "tokens_out": 1})


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), mock.patch.object(out, "reconfigure", create=True):
        code = check.main(list(argv))
    return code, out.getvalue()


@mock.patch.dict(os.environ, {"CODEOWN_VOTES": "1"})  # mỗi câu một phiếu: test đếm số lần gọi model
class CheckCliTest(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.dir = tempfile.TemporaryDirectory()
        os.chdir(self.dir.name)
        with open("attr.json", "w", encoding="utf-8") as f:
            json.dump({"task_id": "t1", "lines": LINES, "di": 30}, f)

    def tearDown(self):
        os.chdir(self.cwd)
        self.dir.cleanup()

    def start(self):
        with model_replies(QUESTIONS):
            return run("check", "start", "--task", "t1", "--from", "attr.json", "--json")

    def test_start_never_prints_rubric_but_keeps_it_in_session(self):
        code, out = self.start()
        self.assertEqual(code, 0)
        self.assertNotIn("rubric_hidden", out)
        self.assertNotIn("BÍ_MẬT", out)
        self.assertEqual(json.loads(out)["questions"][0]["qid"], "q1")
        self.assertIn("BÍ_MẬT", check.load_session("t1")["questions"][0]["rubric_hidden"])

    def test_two_graded_rounds_then_final(self):
        self.start()
        answer = ["check", "answer", "--task", "t1", "--qid", "q1", "--text", "Để không bị đoán mật khẩu qua thời gian."]
        with model_replies(PARTIAL, PARTIAL):
            r1 = json.loads(run(*answer)[1])
            r2 = json.loads(run(*answer)[1])
        code, out = run(*answer)
        self.assertEqual((r1["round"], r1["final"], r2["round"], r2["final"]), (1, False, 2, True))
        self.assertEqual(code, 1)
        self.assertIn("đã chấm xong", json.loads(out)["error"])

    def test_retry_after_dont_know_does_not_use_a_round(self):
        self.start()
        run("check", "answer", "--task", "t1", "--qid", "q1", "--text", "không biết")
        with model_replies(PARTIAL):
            _, out = run("check", "answer", "--task", "t1", "--qid", "q1", "--text", "Để không bị đoán qua thời gian.")
        self.assertEqual(json.loads(out)["round"], 1)

    def test_unknown_task_is_an_error(self):
        code, out = run("check", "answer", "--task", "nope", "--qid", "q1", "--text", "x")
        self.assertEqual(code, 1)
        self.assertIn("error", json.loads(out))

    def test_ledger_save_writes_last_graded_label(self):
        self.start()
        with model_replies(PARTIAL):
            run("check", "answer", "--task", "t1", "--qid", "q1", "--text", "Để không bị đoán qua thời gian.")
        code, out = run("ledger", "save", "--task", "t1", "--json")
        self.assertEqual((code, json.loads(out)), (0, {"ok": True, "saved": 1}))
        self.assertEqual(ledger.weak_concepts(), set())
        self.assertEqual(ledger.recent_understood(), set())

    def test_skip_when_below_threshold(self):
        with open("attr.json", "w", encoding="utf-8") as f:
            json.dump({"task_id": "t1", "lines": LINES[:3] + [dict(l, label="nguoi_viet") for l in LINES], "di": 30}, f)
        code, out = run("check", "start", "--task", "t1", "--from", "attr.json")
        self.assertIn("skip", json.loads(out))


if __name__ == "__main__":
    unittest.main()
