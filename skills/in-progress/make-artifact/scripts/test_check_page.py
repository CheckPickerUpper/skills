"""Behavioral tests of check_page.py at its command line."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "check_page.py"

STEPS_WITH_STATUS = """\
<h1>Every ability step</h1>
<table>
  <tr><th>Step</th><th>Server</th></tr>
  <tr><td><code>ownCue</code></td><td><span class="chip">built</span></td></tr>
  <tr><td><code>lockTag</code></td><td><span class="chip">not built</span> #1153</td></tr>
  <tr><td><code>drain</code></td><td><span class="chip">built</span></td></tr>
  <tr><td><code>pickTarget</code></td><td><span class="chip">built</span></td></tr>
</table>
<a href="https://example.com/issues/1153">source</a>
"""

STEPS_WITHOUT_STATUS = """\
<h1>Every ability step</h1>
<table>
  <tr><th>Step</th><th>Server</th></tr>
  <tr><td><code>ownCue</code></td><td>instant</td></tr>
  <tr><td><code>lockTag</code></td><td>server only #1153</td></tr>
  <tr><td><code>drain</code></td><td>instant</td></tr>
  <tr><td><code>pickTarget</code></td><td>instant</td></tr>
</table>
<a href="https://example.com/issues/1153">source</a>
"""


class CheckPage(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)

    def page(self, name, html):
        path = self.folder / name
        path.write_text(html, encoding="utf-8")
        return path

    def check(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            capture_output=True, text=True, timeout=10,
        )

    def test_plain_code_block_is_refused_with_its_line(self):
        page = self.page("page.html", "<p>Before</p>\n<pre><code>ReadBody(): Body</code></pre>")
        result = self.check(page)
        self.assertEqual(result.returncode, 1)
        self.assertIn("1 code blocks have no syntax colouring", result.stdout)
        self.assertIn("line 2: ReadBody(): Body", result.stdout)

    def test_code_block_with_coloured_spans_passes(self):
        page = self.page(
            "page.html",
            '<pre><code><span class="fn">ReadBody</span>(): <span class="ty">Body</span></code></pre>',
        )
        result = self.check(page)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_code_block_coloured_by_a_page_script_passes(self):
        page = self.page("page.html", '<pre><code class="language-ts">ReadBody(): Body</code></pre>')
        self.assertEqual(self.check(page).returncode, 0)

    def test_inline_code_in_a_sentence_is_not_a_code_block(self):
        page = self.page("page.html", "<p>Call <code>ReadBody</code> first.</p>")
        self.assertEqual(self.check(page).returncode, 0)

    def test_revision_that_drops_a_status_chip_is_refused(self):
        old = self.page("old.html", STEPS_WITH_STATUS)
        new = self.page("new.html", STEPS_WITHOUT_STATUS)
        result = self.check(new, "--previous", old)
        self.assertEqual(result.returncode, 1)
        self.assertIn("1 things the previous version showed are gone", result.stdout)
        self.assertIn("repeated label: built", result.stdout)

    def test_label_used_once_is_not_held_as_a_page_dimension(self):
        old = self.page("old.html", STEPS_WITH_STATUS)
        new = self.page("new.html", STEPS_WITH_STATUS.replace("not built", "missing"))
        self.assertEqual(self.check(new, "--previous", old).returncode, 0)

    def test_dropped_link_issue_code_name_and_column_are_each_named(self):
        old = self.page("old.html", STEPS_WITH_STATUS)
        new = self.page("new.html", "<h1>Every ability step</h1><p>All built.</p>")
        result = self.check(new, "--previous", old)
        self.assertEqual(result.returncode, 1)
        for entry in (
            "link: https://example.com/issues/1153",
            "issue: #1153",
            "code name: lockTag",
            "column: Server",
        ):
            self.assertIn(entry, result.stdout)
        self.assertNotIn("repeated label: built", result.stdout)

    def test_dropped_entry_with_a_recorded_reason_passes(self):
        old = self.page("old.html", STEPS_WITH_STATUS)
        new = self.page("new.html", STEPS_WITHOUT_STATUS)
        self.page("new.html.dropped.txt", "built: reader said 'remove the status chips'\n")
        self.assertEqual(self.check(new, "--previous", old).returncode, 0)

    def test_dropped_entry_listed_without_a_reason_is_still_refused(self):
        old = self.page("old.html", STEPS_WITH_STATUS)
        new = self.page("new.html", STEPS_WITHOUT_STATUS)
        self.page("new.html.dropped.txt", "built\nbuilt: \n")
        self.assertEqual(self.check(new, "--previous", old).returncode, 1)

    def test_missing_page_exits_2(self):
        self.assertEqual(self.check(self.folder / "absent.html").returncode, 2)


if __name__ == "__main__":
    unittest.main()
