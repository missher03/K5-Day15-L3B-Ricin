import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import ai
from codeown import done, ledger

LINES = [{"file": "app/auth.py", "line": 40 + i, "code": "if token is None: raise", "label": "ai_giu_nguyen"}
         for i in range(25)]


@mock.patch.object(ai, "MODEL_PROVIDER", "fake")
class DoneTest(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.dir = tempfile.TemporaryDirectory()
        os.chdir(self.dir.name)
        with open("attr.json", "w", encoding="utf-8") as f:
            json.dump({"task_id": "t1", "lines": LINES, "di": 30}, f)

    def tearDown(self):
        os.chdir(self.cwd)
        self.dir.cleanup()

    def run_done(self, *answers):
        replies = iter(answers)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = done.run("t1", "attr.json", ask=lambda prompt="": next(replies))
        return code, out.getvalue()

    def test_full_flow_and_save(self):
        # fake chấm mot_phan: vòng 1 chưa xong, vòng 2 kết thúc câu; rồi đồng ý lưu
        code, out = self.run_done("không biết", "Kiểm token rỗng để chặn request lạ", "Vẫn là kiểm token", "y")
        self.assertEqual(code, 0)
        self.assertIn("Gợi ý: Thử đọc lại dòng", out)
        self.assertIn("# Reflect · t1", out)
        self.assertIn("Đã lưu 1 khái niệm.", out)

    def test_declining_save_writes_nothing(self):
        _, out = self.run_done("", "n")
        self.assertIn("Không lưu.", out)
        self.assertFalse(os.path.exists(ledger.LEDGER))


if __name__ == "__main__":
    unittest.main()
