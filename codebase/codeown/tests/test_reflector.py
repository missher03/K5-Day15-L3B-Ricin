import json
import os
import re
import tempfile
import unittest
from unittest import mock

import ai
from codeown import llm, reflector

EVENTS = [
    {"id": "ev_000001", "event": "prompt", "branch": "fix/login", "prompt": "sửa lỗi đăng nhập"},
    {"id": "ev_000002", "event": "ai_edit", "file": "app/pay.py"},
    {"id": "ev_000003", "event": "commit", "meta": {"message": "thêm thanh toán"}},
]
LINES = [{"file": "app/pay.py", "line": 10 + i, "code": "charge(card)", "label": "ai_giu_nguyen"} for i in range(5)]
RESULTS = [{"qid": "q1", "file": "app/pay.py", "lines": [10, 14], "concept": "idempotency key",
            "question": "Vì sao?", "label": "chua_hieu", "missing_concept": "idempotency key"}]


def report(*claims, questions=()):
    return {"sections": [{"title": "Mục đích task", "claims": [{"text": t, "sources": s} for t, s in claims],
                          "questions": list(questions)}]}


def model_replies(*payloads):
    replies = iter(payloads)
    return mock.patch.object(llm, "call_model", side_effect=lambda *a, **k: {
        "text": json.dumps(next(replies), ensure_ascii=False), "model": "m", "tokens_in": 1, "tokens_out": 1})


class ReflectTest(unittest.TestCase):
    def reflect(self, payload):
        with model_replies(payload) as call:
            out = reflector.reflect("t1", EVENTS, LINES, RESULTS)
        return out, call

    def test_claim_with_fake_event_is_removed(self):
        out, _ = self.reflect(report(("Bạn sửa đăng nhập.", ["log#ev_999999"]), ("Task thêm code thanh toán.", ["app/pay.py:10-14"])))
        self.assertNotIn("sửa đăng nhập", out["markdown"])
        self.assertIn("thanh toán. [app/pay.py:10-14]", out["markdown"])
        self.assertEqual(out["sources"], ["app/pay.py:10-14"])

    def test_claim_citing_line_outside_diff_is_removed(self):
        out, _ = self.reflect(report(("Dòng 99 gọi API.", ["app/pay.py:99"])))
        self.assertNotIn("Dòng 99", out["markdown"])

    def test_intent_mismatch_kept_with_both_sources(self):
        out, _ = self.reflect(report(("Nhánh nói sửa đăng nhập nhưng commit nói thêm thanh toán.",
                                      ["log#ev_000001", "[log#ev_000003]"])))
        self.assertIn("[log#ev_000001] [log#ev_000003]", out["markdown"])

    def test_duplicate_sources_rendered_once(self):
        out, _ = self.reflect(report(("A.", ["log#ev_000001", "[log#ev_000001]"])))
        self.assertIn("- A. [log#ev_000001]\n", out["markdown"])

    def test_questions_survive_without_sources(self):
        out, _ = self.reflect(report(questions=["Vì sao chọn thư viện stripe?"]))
        self.assertIn("Vì sao chọn thư viện stripe?", out["markdown"])

    def test_every_rendered_claim_has_a_source(self):
        out, _ = self.reflect(report(("A.", ["log#ev_000002"]), ("B.", []), ("C.", ["docs:data/docs/khong-co.md"])))
        claims = [l for l in out["markdown"].splitlines() if l.startswith("- ")]
        self.assertTrue(claims)
        self.assertTrue(all(re.search(r"\[[^\]]+\]$", l) for l in claims))

    def test_intent_sources_and_no_rubric_sent(self):
        _, call = self.reflect(report())
        user = call.call_args[0][1]
        for ref in ("[log#ev_000001] nhánh: fix/login", "[log#ev_000003] commit message: thêm thanh toán",
                    "[log#ev_000001] prompt: sửa lỗi đăng nhập"):
            self.assertIn(ref, user)
        self.assertNotIn("rubric", user.lower())

    def test_docs_source_must_exist(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "data", "docs"))
            open(os.path.join(root, "data", "docs", "hmac.md"), "w").close()
            self.assertTrue(reflector.source_ok("docs:data/docs/hmac.md", set(), {}, root))
            self.assertFalse(reflector.source_ok("docs:data/docs/nope.md", set(), {}, root))
            self.assertFalse(reflector.source_ok("docs:../secret.md", set(), {}, root))
            open(os.path.join(root, "secret.md"), "w").close()
            self.assertFalse(reflector.source_ok("docs:data/docs/../../secret.md", set(), {}, root))

    def test_prompt_has_no_unfilled_placeholders(self):
        self.assertNotIn("{{", llm.load_prompt("reflector", FENCE="DATA_0000"))

    @mock.patch.object(ai, "MODEL_PROVIDER", "fake")
    def test_fake_mode_cites_a_real_source(self):
        out = reflector.reflect("t1", EVENTS, LINES, RESULTS)
        self.assertEqual(out["sources"], ["log#ev_000001"])


if __name__ == "__main__":
    unittest.main()
