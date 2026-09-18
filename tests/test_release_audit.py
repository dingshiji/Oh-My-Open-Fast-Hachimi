"""Publication guard regression tests; each Git repository is temporary."""
import contextlib
import importlib.util
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "audit_release", Path(__file__).resolve().parents[1] / "scripts/audit_release.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ReleaseAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-q")

    def tearDown(self):
        # Git makes loose objects read-only on Windows.
        import os
        import stat
        for directory, _, files in os.walk(self.root):
            for name in files:
                os.chmod(Path(directory) / name, stat.S_IWRITE | stat.S_IREAD)
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-c", f"safe.directory={self.root.as_posix()}",
             "-c", "user.name=Audit Test", "-c", "user.email=audit@example.invalid",
             *args], cwd=self.root, stderr=subprocess.STDOUT)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")

    def check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return audit.audit(self.root)

    def test_clean_description_and_audio_exception(self):
        self.write("models/DOWNLOAD.txt", "Download models separately.")
        self.write("tools/local/README.txt", "Local applications only.")
        self.write("examples/demo.wav", "fixture")
        self.assertEqual(self.check(), 0)

    def test_ignored_file_is_not_published_but_force_added_file_fails(self):
        self.write(".gitignore", "config/local.json\n")
        self.write("config/local.json", "{}")
        self.assertEqual(self.check(), 0)
        self.git("add", "-f", "config/local.json")
        self.assertEqual(self.check(), 1)

    def test_staged_secret_detected_after_worktree_is_cleaned(self):
        self.write("settings.txt", "gh" + "p_" + "A" * 36)
        self.git("add", "settings.txt")
        self.write("settings.txt", "clean")
        self.assertEqual(self.check(), 1)

    def test_deleted_historical_binary_is_still_detected(self):
        self.write("hidden/character.blend", "private")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.git("rm", "-q", "hidden/character.blend")
        self.git("commit", "-qm", "remove")
        self.assertEqual(self.check(), 1)

    def test_personal_path_and_secret_never_print_contents(self):
        self.write("settings.txt", "C:" + "/Users/" + "example-person/private\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(audit.audit(self.root), 1)
        self.assertNotIn("example-person", output.getvalue())


if __name__ == "__main__":
    unittest.main()
