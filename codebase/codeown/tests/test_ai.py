import unittest
from unittest import mock

import ai

OK = {"stop_reason": "end_turn", "content": [{"type": "text", "text": "{}"}],
      "usage": {"input_tokens": 12, "output_tokens": 3}}


class CallModelTest(unittest.TestCase):
    def call(self, response, **kw):
        with mock.patch.object(ai, "MODEL_PROVIDER", "anthropic"), \
             mock.patch.object(ai, "post_json", return_value=response) as post:
            res = ai.call_model("sys", "user", **kw)
        return res, post.call_args[0][2]

    def test_tier_schema_and_effort_reach_the_request(self):
        res, body = self.call(OK, model="small", schema={"type": "object"}, effort="low")
        self.assertEqual(body["model"], ai.TIERS["small"])
        self.assertEqual(body["output_config"], {"format": {"type": "json_schema", "schema": {"type": "object"}},
                                                 "effort": "low"})
        self.assertNotIn("temperature", body)
        self.assertEqual((res["model"], res["tokens_in"], res["tokens_out"]), (ai.TIERS["small"], 12, 3))

    def test_old_two_argument_call_still_works(self):
        res, body = self.call(OK)
        self.assertNotIn("output_config", body)
        self.assertEqual(res["model"], ai.MODEL_NAME)

    def test_refusal_and_truncation_raise(self):
        for reason in ("refusal", "max_tokens"):
            with self.assertRaises(ai.ModelStopped):
                self.call(dict(OK, stop_reason=reason), model="strong")


if __name__ == "__main__":
    unittest.main()
