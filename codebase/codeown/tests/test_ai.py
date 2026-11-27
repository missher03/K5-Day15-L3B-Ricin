import io
import unittest
import urllib.error
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


GROQ_OK = {"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
           "usage": {"prompt_tokens": 20, "completion_tokens": 7}}


class GroqTest(unittest.TestCase):
    def call(self, response, **kw):
        with mock.patch.object(ai, "MODEL_PROVIDER", "groq"),              mock.patch.object(ai, "post_json", return_value=response) as post:
            res = ai.call_model("sys", "user", **kw)
        return res, post.call_args[0]

    def test_strict_schema_effort_and_usage(self):
        res, (url, headers, body) = self.call(GROQ_OK, model="strong", schema={"type": "object"}, effort="medium")
        self.assertEqual(url, ai.URL_GROQ)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        self.assertEqual(body["model"], ai.TIERS["strong"])
        self.assertEqual(body["messages"][0], {"role": "system", "content": "sys"})
        self.assertEqual(body["response_format"]["json_schema"], {"name": "out", "strict": True,
                                                                  "schema": {"type": "object"}})
        self.assertEqual((body["reasoning_effort"], body["temperature"]), ("medium", 0))
        self.assertEqual((res["text"], res["model"], res["tokens_in"], res["tokens_out"]),
                         ("{}", ai.TIERS["strong"], 20, 7))

    def test_json_validate_failed_is_retried_once(self):
        bad = RuntimeError('HTTP 400: {"error":{"code":"json_validate_failed"}}')
        with mock.patch.object(ai, "MODEL_PROVIDER", "groq"),                 mock.patch.object(ai, "post_json", side_effect=[bad, GROQ_OK]) as post:
            self.assertEqual(ai.call_model("s", "u", model="small")["text"], "{}")
        self.assertEqual(post.call_count, 2)
        with mock.patch.object(ai, "MODEL_PROVIDER", "groq"),                 mock.patch.object(ai, "post_json", side_effect=[bad, bad]), self.assertRaises(RuntimeError):
            ai.call_model("s", "u", model="small")

    def test_truncated_output_raises(self):
        bad = dict(GROQ_OK, choices=[{"finish_reason": "length", "message": {"content": "{"}}])
        with self.assertRaises(ai.ModelStopped):
            self.call(bad, model="small")


class RateLimitTest(unittest.TestCase):
    def test_429_waits_retry_after_then_succeeds(self):
        limited = urllib.error.HTTPError("u", 429, "rate", {"retry-after": "2"}, io.BytesIO(b"{}"))
        ok = mock.MagicMock()
        ok.__enter__.return_value.read.return_value = b'{"x": 1}'
        with mock.patch("urllib.request.urlopen", side_effect=[limited, ok]), \
                mock.patch.object(ai.time, "sleep") as sleep:
            self.assertEqual(ai.post_json(ai.URL_GROQ, {}, {}), {"x": 1})
        sleep.assert_called_once_with(2.5)

    def test_other_http_errors_raise_at_once(self):
        bad = urllib.error.HTTPError("u", 400, "bad", {}, io.BytesIO(b"oops"))
        with mock.patch("urllib.request.urlopen", side_effect=[bad]), self.assertRaises(RuntimeError):
            ai.post_json(ai.URL_GROQ, {}, {})


if __name__ == "__main__":
    unittest.main()
