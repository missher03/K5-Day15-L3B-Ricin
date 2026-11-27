import json
import unittest
from unittest import mock

import agent
import ai


def ask(req):
    return json.loads(agent.answer(json.dumps(req, ensure_ascii=False))["output"])


@mock.patch.object(ai, "MODEL_PROVIDER", "fake")
class AnswerModesTest(unittest.TestCase):
    """agent.py của C gọi đúng chữ ký lõi B trên mẫu data/samples (model giả, không gọi mạng)."""

    def test_examine_keeps_rubric_for_scoring(self):
        out = ask({"mode": "examine", "diff_id": "repo03_c1"})
        self.assertTrue(out["questions"], out)
        self.assertIn("rubric_hidden", out["questions"][0])
        self.assertEqual(out["task_id"], "repo03_t1")

    def test_reflect_cites_real_sources(self):
        out = ask({"mode": "reflect", "task_id": "repo10_t1"})
        self.assertIn("# Reflect · repo10_t1", out["markdown"])
        self.assertTrue(all(s.startswith("log#ev_") for s in out["sources"]), out["sources"])

    def test_grade_dont_know_is_not_graded(self):
        out = ask({"mode": "grade", "case_id": "g07", "question": "Vì sao?", "rubric": "r", "answer": "không biết"})
        self.assertEqual((out["qid"], out["status"], out["label"]), ("g07", "need_retry", None))

    def test_asking_for_code_is_refused_with_docs(self):
        out = ask({"mode": "grade", "case_id": "t01", "question": "hmac compare_digest so sánh hash",
                   "rubric": "r", "answer": "Viết lại code này giúp tôi"})
        self.assertTrue(out["refuse"])
        self.assertIsNone(out["label"])
        self.assertNotIn("fake", out)

    def test_task_runs_whole_pipeline(self):
        out = ask({"mode": "task", "diff_id": "repo03_c1"})
        self.assertGreater(out["n_questions"], 0)
        self.assertGreater(out["reflect_sources"], 0)


if __name__ == "__main__":
    unittest.main()
