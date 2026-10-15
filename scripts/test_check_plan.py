import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
import check_plan  # noqa: E402
from check_plan import check  # noqa: E402


class CheckPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = os.path.join(cls.tmp.name, "repo")
        os.makedirs(os.path.join(cls.repo, "app"))
        with open(os.path.join(cls.repo, "app", "a.php"), "w") as f:
            f.write("1\n2\n3\n")
        git = ["git", "-C", cls.repo, "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["commit", "-qm", "x"], check=True)
        cls.sha = subprocess.check_output(git + ["rev-parse", "--short", "HEAD"], text=True).strip()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_check(self, text, env=None):
        return check(text, self.repo, env or {})

    def test_valid_path_and_line(self):
        self.assertEqual(self.run_check("See `app/a.php` and `app/a.php:3`."), [])

    def test_directory_ok(self):
        self.assertEqual(self.run_check("`app/` and `app`"), [])
        self.assertEqual(len(self.run_check("`app/:3`")), 1)

    def test_version_and_glob_ignored(self):
        self.assertEqual(self.run_check("PHP `8.3`, `1.2.3`, `app/*.php`."), [])

    def test_line_range(self):
        self.assertEqual(self.run_check("`app/a.php:1-3`"), [])
        self.assertEqual(len(self.run_check("`app/a.php:2-9`")), 1)
        self.assertEqual(len(self.run_check("`app/a.php:3-2`")), 1)

    def test_fence_skipped(self):
        self.assertEqual(self.run_check("```\n`app/nope.php`\n```\n"), [])

    def test_missing_path(self):
        self.assertEqual(len(self.run_check("`app/nope.php`")), 1)

    def test_line_out_of_range(self):
        self.assertEqual(len(self.run_check("`app/a.php:4`")), 1)
        self.assertEqual(len(self.run_check("`app/a.php:0`")), 1)

    def test_escape_rejected(self):
        self.assertEqual(len(self.run_check("`../outside.txt`")), 1)
        self.assertEqual(len(self.run_check("`/etc/passwd`")), 1)

    def test_command_token_ignored(self):
        self.assertEqual(self.run_check("Run `composer install` and `https://x.com/a.php`."), [])

    def test_missing_auth_with_links(self):
        text = "[P](https://x.atlassian.net/wiki/spaces/S/pages/123/Title)"
        out = self.run_check(text)
        self.assertEqual(len(out), 1)
        self.assertIn("CONFLUENCE_AUTH", out[0])

    ENV = {"CONFLUENCE_AUTH": "SECRETTOKEN", "CONFLUENCE_SERVER": "https://x.atlassian.net"}
    LINK = "[P](https://x.atlassian.net/wiki/spaces/S/pages/123/Title)"

    def test_link_ok(self):
        resp = mock.MagicMock()
        resp.__enter__.return_value.status = 200
        with mock.patch.object(check_plan._opener, "open", return_value=resp):
            self.assertEqual(self.run_check(self.LINK, self.ENV), [])

    def test_link_redirect_blocked(self):
        err = urllib.error.HTTPError("u", 302, "Found", {}, None)
        with mock.patch.object(check_plan._opener, "open", side_effect=err):
            out = self.run_check(self.LINK, self.ENV)
        self.assertEqual(out, ["page 123: HTTP 302"])
        self.assertNotIn("SECRETTOKEN", "".join(out))

    def test_redirect_handler_returns_none(self):
        h = check_plan._NoRedirect()
        self.assertIsNone(h.redirect_request(None, None, 302, "Found", {}, "https://evil"))

    def test_link_host_mismatch(self):
        text = "[P](https://other.atlassian.net/wiki/spaces/S/pages/123/T)"
        with mock.patch.object(check_plan._opener, "open") as op:
            out = self.run_check(text, self.ENV)
        self.assertIn("host", out[0])
        op.assert_not_called()

    def test_server_must_be_https(self):
        env = dict(self.ENV, CONFLUENCE_SERVER="http://x.atlassian.net")
        self.assertIn("https", self.run_check(self.LINK, env)[0])

    def test_docs_header(self):
        good = f"## Docs to update\n\nFound on 2026-10-15 from the code on `main` at `{self.sha}`.\n"
        self.assertEqual(self.run_check(good), [])
        bad = "## Docs to update\n\nFound on 2026-10-15 at `deadbee`.\n"
        self.assertEqual(len(self.run_check(bad)), 1)


if __name__ == "__main__":
    unittest.main()
