import os
import tempfile
import time
import unittest

from codeown import ledger


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, ".codeown", "ledger.jsonl")

    def tearDown(self):
        self.dir.cleanup()

    def save(self, task_id, *pairs):
        ledger.save(task_id, [{"concept": c, "label": l} for c, l in pairs], path=self.path)
        time.sleep(0.002)  # mỗi lần lưu một ts khác

    def test_missing_file_reads_empty(self):
        self.assertEqual(ledger.recent_understood(path=self.path), set())
        self.assertEqual(ledger.weak_concepts(path=self.path), set())

    def test_saving_same_task_twice_is_idempotent(self):
        self.save("t1", ("Hash mật khẩu", "hieu"), ("CSRF", "chua_hieu"))
        once = (ledger.recent_understood(path=self.path), ledger.weak_concepts(path=self.path))
        self.save("t1", ("Hash mật khẩu", "hieu"), ("CSRF", "chua_hieu"))
        twice = (ledger.recent_understood(path=self.path), ledger.weak_concepts(path=self.path))
        self.assertEqual(once, twice)

    def test_resave_replaces_earlier_save(self):
        self.save("t1", ("csrf", "chua_hieu"))
        self.save("t1", ("csrf", "hieu"))
        self.assertEqual(ledger.weak_concepts(path=self.path), set())
        self.assertEqual(ledger.recent_understood(path=self.path), {"csrf"})

    def test_recent_understood_counts_tasks_not_lines(self):
        self.save("t1", ("a", "hieu"))
        self.save("t2", ("b", "hieu"), ("c", "hieu"), ("d", "hieu"))
        self.save("t3", ("e", "hieu"))
        self.assertEqual(ledger.recent_understood(n=2, path=self.path), {"b", "c", "d", "e"})

    def test_weak_concept_cleared_when_later_understood(self):
        self.save("t1", ("SQL injection", "chua_hieu"), ("timeout", "chua_hieu"))
        self.save("t2", ("sql   injection", "hieu"))
        self.assertEqual(ledger.weak_concepts(path=self.path), {"timeout"})


if __name__ == "__main__":
    unittest.main()
