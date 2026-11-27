import unittest

from codeown.guard import leaks_answer, safe_hint

RUBRIC = ("Dùng hmac.compare_digest để so sánh hash mật khẩu trong thời gian hằng, "
          "tránh tấn công đo thời gian (timing attack).")

# 6 ví dụ tự viết, chờ C thay bằng 6 ví dụ chuẩn: 3 lộ, 3 sạch.
LEAKS = [
    "Bạn chỉ cần viết:\nif hmac.compare_digest(a, b):\n    return True",
    "```python\nhmac.compare_digest(h1, h2)\n```",
    "Dùng hmac.compare_digest để so sánh hash trong thời gian hằng, tránh timing attack.",
]
CLEAN = [
    "Thử nghĩ: nếu phép so sánh dừng ở ký tự sai đầu tiên thì kẻ tấn công quan sát được gì?",
    "Dòng 44 khác gì so với dùng toán tử == thông thường?",
    "Hàm ở dòng 44 nhận vào hai giá trị nào, và chúng đến từ đâu?",
]


class GuardTest(unittest.TestCase):
    def test_leaking_hints_are_caught(self):
        for text in LEAKS:
            self.assertTrue(leaks_answer(text, RUBRIC), text)

    def test_guiding_hints_pass(self):
        for text in CLEAN:
            self.assertFalse(leaks_answer(text, RUBRIC), text)

    def test_single_code_line_is_not_a_leak(self):
        self.assertFalse(leaks_answer("Xem lại lời gọi ở dòng 44:\nkết quả của nó được dùng ở đâu?", RUBRIC))

    def test_empty_text_is_safe(self):
        self.assertFalse(leaks_answer("", RUBRIC))
        self.assertFalse(leaks_answer(None, RUBRIC))

    def test_safe_hint_never_leaks(self):
        hint = safe_hint("so sánh thời gian hằng", [40, 48])
        self.assertIn("40–48", hint)
        self.assertFalse(leaks_answer(hint, RUBRIC))


if __name__ == "__main__":
    unittest.main()
