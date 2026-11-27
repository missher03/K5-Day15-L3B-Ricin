"""Test phần A (Monitor). Chạy: python -m unittest discover -s tests -v   (chỉ thư viện chuẩn)."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"
os.environ["CODEOWN_CLASSIFIER"] = "rules"

from codeown import events as E  # noqa: E402
from codeown import attribution as A  # noqa: E402
from codeown import dependence as D  # noqa: E402
from codeown import hook as H  # noqa: E402
from codeown import install as I  # noqa: E402
from codeown import monitor as M  # noqa: E402
from codeown import nudge as N  # noqa: E402
from codeown.classifier import classify_rules  # noqa: E402


def ev(event, ts, **kw):
    e = E.make_event(event, ts=ts, **kw)
    e["id"] = kw.get("id") or "ev_%s_%s" % (event, ts[-8:].replace(":", ""))
    return e


def ts(sec):
    return "2026-11-27T20:%02d:%02d+07:00" % (sec // 60, sec % 60)


class TestRedact(unittest.TestCase):
    def test_secrets_are_hidden(self):
        cases = [
            "key sk-ant-api03-abcdefghijklmnopqrstuv",
            "token ghp_abcdefghijklmnopqrstuvwxyz0123",
            "aws AKIAABCDEFGHIJKLMNOP",
            "password=hunter2",
            'API_KEY: "abc123xyz"',
            "Authorization eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N",
        ]
        for c in cases:
            out = E.redact(c)
            self.assertIn(E.REDACTED, out, c)
        self.assertNotIn("hunter2", E.redact("password=hunter2"))

    def test_normal_text_unchanged(self):
        t = "sửa hàm login trả 401 khi sai mật khẩu"
        self.assertEqual(E.redact(t), t)

    def test_prompt_truncated_and_redacted(self):
        e = E.make_event("prompt", prompt="sk-" + "a" * 30 + " " + "x" * 2000)
        self.assertLessEqual(len(e["prompt"]), E.PROMPT_MAX)
        self.assertTrue(e["prompt"].startswith(E.REDACTED))


class TestHashing(unittest.TestCase):
    def test_hash_ignores_indent(self):
        self.assertEqual(E.line_hash("    return x"), E.line_hash("return x\t"))

    def test_trivial_lines(self):
        for t in ["", "   ", "}", "});", ")", "]", "else:", "pass"]:
            self.assertTrue(E.is_trivial(t), repr(t))
        self.assertFalse(E.is_trivial("x = 1"))

    def test_meaningful_lines(self):
        self.assertEqual(E.meaningful_lines("def f():\n\n    return 1\n}\n"), ["def f():", "return 1"])


PATCH = """diff --git a/app/auth.py b/app/auth.py
index 000..111 100644
--- a/app/auth.py
+++ b/app/auth.py
@@ -0,0 +1,6 @@
+import hmac
+def check(pw, stored):
+    return hmac.compare_digest(hash_pw(pw), stored)
+
+def hash_pw(pw):
+    return sha256(pw.encode()).hexdigest()
diff --git a/tests/test_auth.py b/tests/test_auth.py
--- /dev/null
+++ b/tests/test_auth.py
@@ -0,0 +1,2 @@
+def test_check():
+    assert check("a", hash_pw("a"))
"""


class TestAttribution(unittest.TestCase):
    def setUp(self):
        ai = ["import hmac", "def check(pw, stored):", "return hmac.compare_digest(hash_pw(pw), stored)",
              "def hash_pw(pw):", "return hashlib.sha256(pw.encode('utf-8')).hexdigest()"]
        self.evs = [ev("ai_edit", ts(0), file="app/auth.py",
                       line_hashes=[E.line_hash(x) for x in ai], meta={"lines": ai})]

    def test_parse_patch_line_numbers(self):
        added = A.parse_patch(PATCH)
        self.assertEqual([(a["file"], a["line"]) for a in added],
                         [("app/auth.py", 1), ("app/auth.py", 2), ("app/auth.py", 3), ("app/auth.py", 5),
                          ("app/auth.py", 6), ("tests/test_auth.py", 1), ("tests/test_auth.py", 2)])

    def test_parse_patch_counts_context_lines(self):
        patch = "+++ b/a.py\n@@ -1,3 +1,4 @@\n x = 1\n-y = 2\n+y = 3\n z = 4\n+w = 5\n"
        self.assertEqual([(a["line"], a["code"]) for a in A.parse_patch(patch)], [(2, "y = 3"), (4, "w = 5")])

    def test_three_labels(self):
        res = A.attribute_patch(PATCH, self.evs)
        got = {(l["file"], l["line"]): l["label"] for l in res["lines"]}
        self.assertEqual(got[("app/auth.py", 1)], "ai_giu_nguyen")
        self.assertEqual(got[("app/auth.py", 3)], "ai_giu_nguyen")
        self.assertEqual(got[("app/auth.py", 6)], "ai_da_sua")        # người sửa dòng AI
        self.assertEqual(got[("tests/test_auth.py", 2)], "nguoi_viet")
        self.assertEqual(res["stats"], {"ai_giu_nguyen": 4, "ai_da_sua": 1, "nguoi_viet": 2})

    def test_no_ai_events_means_all_human(self):
        res = A.attribute_patch(PATCH, [])
        self.assertEqual(res["stats"]["nguoi_viet"], 7)


class TestClassifierRules(unittest.TestCase):
    def test_labels(self):
        cases = {
            "viết cho tôi API CRUD sản phẩm bằng Flask": "lam_ho",
            "implement login with JWT": "lam_ho",
            "useEffect là gì, khi nào nên dùng?": "hoi_khai_niem",
            "why does python use GIL": "hoi_khai_niem",
            "Traceback (most recent call last):\n  File \"a.py\", line 3\nKeyError: 'id'": "debug_dan_loi",
            "TypeError: undefined is not a function, tôi nghĩ do chưa import": "debug_co_gia_thuyet",
            "ok cảm ơn": "khac",
        }
        for text, want in cases.items():
            self.assertEqual(classify_rules(text), want, text)


class TestDependence(unittest.TestCase):
    def test_formula_extremes(self):
        hi = {"f1": 1, "f2": 1, "f3": 5, "f4_sec": 0, "f5": 0}
        lo = {"f1": 0, "f2": 0, "f3": 0, "f4_sec": 600, "f5": 1}
        self.assertEqual(D.di_from_features(hi), 100)
        self.assertEqual(D.di_from_features(lo), 0)

    def test_formula_known_value(self):
        f = {"f1": 0.8, "f2": 0.5, "f3": 1, "f4_sec": 300, "f5": 0}
        # 100 × (0,24 + 0,125 + 0,04 + 0,075 + 0,1) = 58
        self.assertEqual(D.di_from_features(f), 58)

    def test_missing_f4_is_neutral(self):
        f = {"f1": 0, "f2": 0, "f3": 0, "f4_sec": None, "f5": 1}
        self.assertEqual(D.di_from_features(f), 8)  # 0,15 × 0,5

    def test_features_from_session(self):
        err = "Traceback ... KeyError: 'user_id' at line 12"
        evs = [
            ev("prompt", ts(0), id="p1", prompt="viết hàm đọc CSV và tính tổng doanh thu"),
            ev("ai_edit", ts(10), file="a.py", line_hashes=["h"] * 3),
            ev("prompt", ts(60), id="p2", prompt=err),
            ev("prompt", ts(90), id="p3", prompt=err + " "),
            ev("commit", ts(130), commit="abc"),
        ]
        att = {"stats": {"ai_giu_nguyen": 8, "ai_da_sua": 2, "nguoi_viet": 1},
               "lines": [{"file": "tests/test_a.py", "line": 1, "code": "x", "label": "nguoi_viet"}]}
        r = D.compute(evs, att, mode="rules")
        f = r["features"]
        self.assertAlmostEqual(f["f1"], 0.8)
        self.assertAlmostEqual(f["f2"], 1.0)
        self.assertEqual(f["f3"], 1)
        self.assertEqual(f["f4_sec"], 120)
        self.assertEqual(f["f5"], 1)
        # 100 × (0,24 + 0,25 + 0,04 + 0,15×0,8 + 0) = 65
        self.assertEqual(r["di"], 65)

    def test_commit_breaks_error_chain(self):
        err = "Error: connection refused port 5432"
        evs = [ev("prompt", ts(0), id="a", prompt=err), ev("commit", ts(5), commit="x"),
               ev("prompt", ts(9), id="b", prompt=err)]
        self.assertEqual(D.compute(evs, None, "rules")["features"]["f3"], 0)

    def test_no_events(self):
        self.assertIsNone(D.compute([], None)["di"])

    def test_test_file_detection(self):
        for p in ["tests/test_a.py", "src/a_test.go", "web/app.spec.ts", "__tests__/x.js", "test_utils.py"]:
            self.assertTrue(D.is_test_file(p), p)
        self.assertFalse(D.is_test_file("src/contest.py"))


class TestNudge(unittest.TestCase):
    def _labels(self, evs):
        return D.compute(evs, None, "rules")["features"]

    def test_same_error_three_times(self):
        err = "ModuleNotFoundError: No module named 'flask'"
        evs = [ev("prompt", ts(i * 20), id="p%d" % i, prompt=err) for i in range(3)]
        n = N.check_nudge(evs, 10, self._labels(evs), now=E.parse_ts(ts(100)))
        self.assertEqual(n["rule"], "lap_loi")

    def test_two_times_not_enough(self):
        err = "ModuleNotFoundError: No module named 'flask'"
        evs = [ev("prompt", ts(i * 20), id="p%d" % i, prompt=err) for i in range(2)]
        self.assertIsNone(N.check_nudge(evs, 10, self._labels(evs), now=E.parse_ts(ts(100))))

    def test_bulk_accept(self):
        evs = [ev("prompt", ts(0), id="p", prompt="giải thích đoạn này"),
               ev("ai_edit", ts(20), file="a.py", line_hashes=["h"] * 55)]
        self.assertEqual(N.check_nudge(evs, 10, self._labels(evs), now=E.parse_ts(ts(60)))["rule"], "nhan_nhieu_dong")

    def test_whole_feature(self):
        evs = [ev("prompt", ts(0), id="p", prompt="viết toàn bộ chức năng giỏ hàng cho tôi")]
        self.assertEqual(N.check_nudge(evs, 10, self._labels(evs), now=E.parse_ts(ts(5)))["rule"], "lam_ho_ca_tinh_nang")

    def test_high_di(self):
        evs = [ev("prompt", ts(0), id="p", prompt="ok")]
        n = N.check_nudge(evs, 75, {"f1": 0.85}, now=E.parse_ts(ts(5)))
        self.assertEqual(n["rule"], "di_cao")
        self.assertIn("85%", n["message"])

    def test_cooldown_15_minutes(self):
        evs = [ev("nudge", ts(0)), ev("prompt", ts(10), id="p", prompt="ok")]
        self.assertIsNone(N.check_nudge(evs, 90, {"f1": 1}, now=E.parse_ts(ts(600))))
        later = E.parse_ts("2026-11-27T20:16:00+07:00")
        self.assertIsNotNone(N.check_nudge(evs, 90, {"f1": 1}, now=later))


def _git(repo, *args):
    subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
                   + list(args), check=True, capture_output=True)


@unittest.skipUnless(shutil.which("git"), "cần git")
class TestEndToEnd(unittest.TestCase):
    """Repo git thật: init → hook Claude Code → commit → status / attribute."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="codeown-")
        _git(self.repo, "init", "-q", "-b", "main")
        with open(os.path.join(self.repo, "README.md"), "w") as f:
            f.write("demo\n")
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "-qm", "init")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def _hook(self, payload, tool="claude_code"):
        payload.setdefault("cwd", self.repo)
        return H.run(tool, stdin=io.StringIO(json.dumps(payload)))

    def test_init_is_idempotent(self):
        r1 = I.init(self.repo, ["claude_code", "cursor"])
        I.init(self.repo, ["claude_code", "cursor"])
        with open(os.path.join(self.repo, ".claude", "settings.json")) as f:
            s = json.load(f)
        self.assertEqual(len(s["hooks"]["UserPromptSubmit"]), 1)
        self.assertEqual(len(s["hooks"]["PostToolUse"]), 1)
        with open(os.path.join(self.repo, ".gitignore")) as f:
            self.assertEqual(f.read().count(".codeown/"), 1)
        with open(os.path.join(self.repo, ".git", "hooks", "post-commit")) as f:
            self.assertEqual(f.read().count("# >>> codeown"), 1)
        self.assertIn(".claude/settings.json", r1["hooks_written"])

    def test_init_keeps_existing_hooks(self):
        os.makedirs(os.path.join(self.repo, ".claude"))
        with open(os.path.join(self.repo, ".claude", "settings.json"), "w") as f:
            json.dump({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo mine"}]}]},
                       "model": "x"}, f)
        I.init(self.repo, ["claude_code"])
        with open(os.path.join(self.repo, ".claude", "settings.json")) as f:
            s = json.load(f)
        self.assertEqual(s["model"], "x")
        self.assertEqual(len(s["hooks"]["Stop"]), 2)

    def test_full_flow(self):
        I.init(self.repo, ["claude_code"])
        code = "def total(rows):\n    s = 0\n    for r in rows:\n        s += float(r['amount'])\n    return s\n"
        self._hook({"hook_event_name": "UserPromptSubmit", "session_id": "s1",
                    "prompt": "viết hàm tính tổng amount, key sk-ant-api03-zzzzzzzzzzzzzzzzzzzz"})
        self._hook({"hook_event_name": "PostToolUse", "session_id": "s1", "tool_name": "Write",
                    "tool_input": {"file_path": os.path.join(self.repo, "calc.py"), "content": code}})
        self._hook({"hook_event_name": "Stop", "session_id": "s1"})
        # người dùng sửa 1 dòng, tự thêm 1 dòng
        user_code = code.replace("float(r['amount'])", "float(r['amount'] or 0)") + "\nTAX = 0.1\n"
        with open(os.path.join(self.repo, "calc.py"), "w") as f:
            f.write(user_code)
        _git(self.repo, "add", "calc.py")
        _git(self.repo, "commit", "-qm", "add total")
        H.run("git", repo=self.repo)  # post-commit (trong test gọi trực tiếp)

        evs = E.read_events(self.repo)
        kinds = [e["event"] for e in evs]
        self.assertEqual(kinds[:3], ["prompt", "ai_edit", "ai_turn_end"])
        self.assertIn("commit", kinds)
        self.assertNotIn("sk-ant", json.dumps(evs))
        self.assertEqual(evs[1]["file"], "calc.py")

        rep = M.attribution_report(self.repo)
        self.assertEqual(rep["stats"], {"ai_giu_nguyen": 4, "ai_da_sua": 1, "nguoi_viet": 1})
        self.assertIsInstance(rep["di"], int)
        st = M.status(self.repo, record_nudge=False)
        self.assertTrue({"task_id", "di", "stats", "features", "pending_nudge"} <= set(st))

    def test_hook_never_raises_on_garbage(self):
        self.assertIsNone(H.run("claude_code", stdin=io.StringIO("{not json")))

    def test_cli_json(self):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "codebase", "codeown_cli.py"), "status",
                              "--repo", self.repo, "--json"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("task_id", json.loads(out.stdout))
        out = subprocess.run([sys.executable, os.path.join(ROOT, "codebase", "codeown_cli.py"), "check", "start",
                              "--json"], capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("error", json.loads(out.stdout))

    def _cli(self, *args):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "codebase", "codeown_cli.py")] + list(args)
                             + ["--repo", self.repo], capture_output=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout.decode("utf-8")

    def test_cli_text_and_jsonl(self):
        I.init(self.repo, ["claude_code"])
        self._hook({"hook_event_name": "UserPromptSubmit", "prompt": "chào bạn, useEffect là gì?"})
        self.assertIn("DI", self._cli("status"))                       # chữ cho người đọc
        log = self._cli("log")
        self.assertIn("chào bạn", log)
        self.assertIn("hoi_khai_niem", log)
        rows = [json.loads(x) for x in self._cli("log", "--jsonl").splitlines()]
        self.assertEqual(rows[0]["event"], "prompt")
        self.assertEqual(len(self._cli("status", "--json").strip().splitlines()), 1)

    def test_stdin_bytes_are_utf8(self):
        """Windows: hook nhận UTF-8 qua stdin; phải giữ đúng chữ Việt."""
        I.init(self.repo, ["claude_code"])
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "chào bạn", "cwd": self.repo},
                             ensure_ascii=False).encode("utf-8")
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        subprocess.run([sys.executable, os.path.join(ROOT, "codebase", "codeown_cli.py"), "hook",
                        "--tool=claude_code"], input=payload, env=env, check=True)
        self.assertEqual(E.read_events(self.repo)[-1]["prompt"], "chào bạn")

    def test_storage_is_jsonl(self):
        I.init(self.repo, ["claude_code"])
        E.new_task(self.repo, "login")
        d = E.codeown_dir(self.repo)
        for name in ("state.jsonl", "config.jsonl"):
            for row in E.load_jsonl(os.path.join(d, name)):
                self.assertIsInstance(row, dict)
            with open(os.path.join(d, name), encoding="utf-8") as f:
                self.assertTrue(all(json.loads(x) for x in f if x.strip()))
        self.assertTrue(E.load_state(self.repo)["task_id"].endswith("_login"))
        self.assertTrue(E.load_state(self.repo)["enabled"])
        self.assertFalse(os.path.exists(os.path.join(d, "state.json")))

    def test_summary_written_after_commit(self):
        I.init(self.repo, ["claude_code"])
        with open(os.path.join(self.repo, "a.py"), "w") as f:
            f.write("x = 1\n")
        _git(self.repo, "add", "a.py")
        _git(self.repo, "commit", "-qm", "a")
        H.run("git", repo=self.repo)
        rows = E.load_jsonl(os.path.join(E.codeown_dir(self.repo), "summary.jsonl"))
        self.assertEqual(rows[-1]["stats"]["nguoi_viet"], 1)


class TestIgnore(unittest.TestCase):
    def test_default_patterns(self):
        pats = A.ignore_patterns()
        for p in [".claude/settings.json", ".gitignore", ".codeown/events.jsonl", "web/package-lock.json",
                  "README.md", "docs/notes.txt", ".github/hooks/hooks.json", ".vscode/settings.json"]:
            self.assertTrue(A.is_ignored(p, pats), p)
        for p in ["sum.py", "src/app.ts", ".github/workflows/ci.yml", "config/settings.json"]:
            self.assertFalse(A.is_ignored(p, pats), p)

    def test_config_ignore_and_unignore(self):
        pats = A.ignore_patterns({"ignore": ["migrations/*"], "unignore": ["*.md"]})
        self.assertTrue(A.is_ignored("migrations/0001_init.py", pats))
        self.assertFalse(A.is_ignored("README.md", pats))

    def test_ignored_files_reported(self):
        patch = "+++ b/.gitignore\n@@ -0,0 +1 @@\n+.codeown/\n+++ b/a.py\n@@ -0,0 +1 @@\n+x = 1\n"
        res = A.attribute_patch(patch, [])
        self.assertEqual(res["stats"]["nguoi_viet"], 1)
        self.assertEqual(res["ignored_files"], [".gitignore"])


@unittest.skipUnless(shutil.which("git"), "cần git")
class TestRepoWithoutCommits(unittest.TestCase):
    def test_branch_known_before_first_commit(self):
        repo = tempfile.mkdtemp(prefix="codeown-")
        try:
            _git(repo, "init", "-q", "-b", "master")
            self.assertEqual(E.current_branch(repo), "master")
            self.assertTrue(E.current_task_id(repo).endswith("_master"))
        finally:
            shutil.rmtree(repo, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(shutil.which("git"), "cần git")
class TestDemoScenario(unittest.TestCase):
    """Đúng ca Quốc thử ngày 27/11: repo trống → init → nhờ viết sum.py → commit tất cả (gồm file init sinh ra)."""

    def test_first_commit_counts_only_ai_file(self):
        repo = tempfile.mkdtemp(prefix="codeown-")
        try:
            _git(repo, "init", "-q", "-b", "master")
            I.init(repo, ["claude_code"])
            code = ("def sum_two(a, b):\n    return a + b\n\n\nif __name__ == \"__main__\":\n"
                    "    x = int(input(\"a = \"))\n    y = int(input(\"b = \"))\n    print(sum_two(x, y))\n")
            for p in ({"hook_event_name": "UserPromptSubmit", "prompt": "chào bạn"},
                      {"hook_event_name": "Stop"},
                      {"hook_event_name": "UserPromptSubmit", "prompt": "viết 1 file sum.py tính tổng 2 số a và b"},
                      {"hook_event_name": "PostToolUse", "tool_name": "Write",
                       "tool_input": {"file_path": os.path.join(repo, "sum.py"), "content": code}},
                      {"hook_event_name": "Stop"}):
                p["cwd"] = repo
                H.run("claude_code", stdin=io.StringIO(json.dumps(p)))
            with open(os.path.join(repo, "sum.py"), "w", newline="\r\n") as f:  # Windows: CRLF
                f.write(code)
            _git(repo, "add", "-A")
            _git(repo, "commit", "-qm", "add sum.py")  # root commit
            H.run("git", repo=repo)
            st = M.status(repo, record_nudge=False)
            self.assertEqual(st["stats"], {"ai_giu_nguyen": 6, "ai_da_sua": 0, "nguoi_viet": 0})
            self.assertIn(".claude/settings.json", st["ignored_files"])
            self.assertIn(".gitignore", st["ignored_files"])
            self.assertEqual(st["features"]["f1"], 1.0)
            self.assertEqual(st["features"]["f2"], 1.0)   # "chào bạn" (khac) không tính
            # 100 × (0,3·1 + 0,25·1 + 0 + 0,15·(1 − f4/600) + 0,1) ≈ 79 khi commit ngay
            self.assertGreaterEqual(st["di"], 70)
        finally:
            shutil.rmtree(repo, ignore_errors=True)
