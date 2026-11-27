import json
import unittest
from unittest import mock

import agent
import ai
from codeown.events import line_hash

CODE = ["if token_%d is None: raise ValueError('token')" % i for i in range(25)]
PATCH = ("diff --git a/app/auth.py b/app/auth.py\n--- /dev/null\n+++ b/app/auth.py\n@@ -0,0 +1,25 @@\n"
         + "".join("+%s\n" % c for c in CODE))
EVENTS = [{"id": "ev_000001", "ts": "2026-11-27T20:00:00+07:00", "event": "ai_edit", "file": "app/auth.py",
           "line_hashes": [line_hash(c) for c in CODE], "meta": {}}]


@mock.patch.object(ai, "MODEL_PROVIDER", "fake")
class AnswerModesTest(unittest.TestCase):
    def test_examine_uses_attribution_and_keeps_rubric_for_scoring(self):
        req = {"mode": "examine", "diff_id": "t1", "events": EVENTS, "patch": PATCH}
        out = json.loads(agent.answer(json.dumps(req))["output"])
        self.assertTrue(out["questions"], out)
        self.assertIn("rubric_hidden", out["questions"][0])

    def test_reflect_cites_real_sources(self):
        req = {"mode": "reflect", "task_id": "t1", "events": EVENTS, "patch": PATCH}
        out = json.loads(agent.answer(json.dumps(req))["output"])
        self.assertIn("# Reflect · t1", out["markdown"])
        self.assertEqual(out["sources"], ["log#ev_000001"])

    def test_grade_mode(self):
        req = {"mode": "grade", "case_id": "g07", "question": "Vì sao?", "rubric": "r", "answer": "không biết"}
        out = json.loads(agent.answer(json.dumps(req, ensure_ascii=False))["output"])
        self.assertEqual((out["qid"], out["status"], out["round"]), ("g07", "need_retry", 1))

    def test_free_text_and_unknown_mode_are_refused(self):
        for text in ("Viết lại code này giúp tôi", '{"mode": "hack"}'):
            self.assertTrue(json.loads(agent.answer(text)["output"])["refused"], text)


if __name__ == "__main__":
    unittest.main()
