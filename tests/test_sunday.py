import os
import subprocess
import tempfile
import unittest

import sunday


class SectionTest(unittest.TestCase):
    def test_section_lists_commits_tests_and_file_tails(self):
        with tempfile.TemporaryDirectory() as d:
            run = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True)
            run("init", "-q")
            open(os.path.join(d, "TODO.md"), "w").write("one\ntwo\nthree\n")
            run("add", "-A")
            run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "first commit")
            pr = {"name": "demo", "branch": "main", "test": "echo 3 passed", "files": {"TODO.md": 2}}
            text = "\n".join(sunday.section(pr, d))
        self.assertIn("commits this week: 1", text)
        self.assertIn("first commit", text)
        self.assertIn("tests: 3 passed", text)
        self.assertIn("two\nthree", text)
        self.assertNotIn("one\n", text)

    def test_missing_test_command_is_said_out_loud(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "-C", d, "init", "-q"], check=True)
            text = "\n".join(sunday.section({"name": "x", "branch": "main"}, d))
        self.assertIn("no test command configured", text)


if __name__ == "__main__":
    unittest.main()
