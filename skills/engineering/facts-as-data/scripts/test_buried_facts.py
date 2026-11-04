"""Tests of buried_facts.py's leads and its check of a census record.

Run with: python3 -m unittest test_buried_facts
"""

import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from buried_facts import leads, main, record_findings

HEADER = "site\tgroup\tmeaning\tdecision\ttable\treaders\tcheck\treason"


def kinds(text, path="src/rule.rs"):
    return [lead.kind for lead in leads(path, text)]


def row(site="src/rule.rs", decision="table", table="catalogue/pause/python.rs",
        readers="deadline_polling_loop", check="build fails on a language with no pause entry",
        reason="-"):
    return dict(site=site, group="pause functions", meaning="calls that pause",
                decision=decision, table=table, readers=readers, check=check, reason=reason)


class Leads(unittest.TestCase):
    def test_a_regex_alternation_of_names_is_a_lead(self):
        text = 'let pause = Regex::new(r"\\b(sleep|usleep|nanosleep)\\b");\n'
        self.assertEqual(kinds(text), ["alternation"])

    def test_two_alternatives_or_symbol_classes_are_not_names(self):
        self.assertEqual(kinds('let a = Regex::new(r"(get|set)");\nlet b = r"(\\d+|\\s+|x)";\n'), [])

    def test_name_checks_chained_with_or_are_a_lead(self):
        text = '(name.contains("sleep") || name.contains("backoff") || name.contains("delay"))\n'
        self.assertEqual(kinds(text), ["alternation"])
        self.assertEqual(kinds('if mode == "fast" or mode == "safe" or mode == "slow":\n', "a.py"),
                         ["alternation"])

    def test_two_chained_checks_are_not(self):
        self.assertEqual(kinds('if a == "x" || b == "y" {\n'), [])

    def test_a_literal_list_of_four_names_is_a_lead_even_across_lines(self):
        text = 'RETRY = [\n    "tenacity",\n    "backoff",\n    "retrying",\n    "stamina",\n]\n'
        found = leads("rules/retry.py", text)
        self.assertEqual([(lead.kind, lead.line) for lead in found], [("list", 1)])

    def test_a_literal_list_of_three_names_is_not(self):
        self.assertEqual(kinds('HOOKS = ["useEffect", "useLayoutEffect", "useInsertionEffect"]\n'), [])

    def test_match_arms_joined_on_literals_are_a_lead(self):
        text = '    "setTimeout" | "setInterval" | "requestAnimationFrame" => Role::Timer,\n'
        self.assertEqual(kinds(text), ["alternation"])

    def test_four_branches_keyed_by_literals_are_a_lead(self):
        text = "match name:\n" + "".join(
            f'    case "{n}":\n        return {i}\n' for i, n in enumerate(["a1", "b2", "c3", "d4"]))
        self.assertEqual(kinds(text, "rules/role.py"), ["branches"])

    def test_three_branches_are_not(self):
        text = "".join(f'    case "{n}":\n        return 1\n' for n in ["a1", "b2", "c3"])
        self.assertEqual(kinds(text, "rules/role.py"), [])


class Record(unittest.TestCase):
    def lead_at(self, path="src/rule.rs"):
        return leads(path, 'let pause = Regex::new(r"(sleep|usleep|nanosleep)");\n')

    def test_a_row_naming_the_file_or_the_line_covers_the_lead(self):
        self.assertEqual(record_findings([row(site="src/rule.rs")], self.lead_at()), [])
        self.assertEqual(record_findings([row(site="src/rule.rs:1")], self.lead_at()), [])
        self.assertEqual(len(record_findings([row(site="src/rule.rs:9")], self.lead_at())), 1)

    def test_a_table_row_names_its_table_readers_and_completeness_check(self):
        for field in ("table", "readers", "check"):
            with self.subTest(field=field):
                self.assertEqual(len(record_findings([row(**{field: "-"})], self.lead_at())), 1)

    def test_a_not_data_row_gives_its_reason_and_names_no_table(self):
        self.assertEqual(len(record_findings([row(decision="not-data")], self.lead_at())), 2)
        bare = row(decision="not-data", table="-", readers="-", check="-", reason="one case")
        self.assertEqual(record_findings([bare], self.lead_at()), [])

    def test_an_unknown_decision_is_a_finding(self):
        self.assertEqual(len(record_findings([row(decision="later")], self.lead_at())), 1)


class Review(unittest.TestCase):
    """--since reports only leads on lines the diff adds, read from a real repository."""

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, *args], check=True, capture_output=True,
                              text=True).stdout.strip()

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(dir=os.environ.get("TEST_SCRATCH"))
        self.repo = self.scratch.name
        self.git("init", "-q")
        Path(self.repo, "rule.py").write_text('OLD = ["a1", "b2", "c3", "d4"]\n')
        self.git("add", "rule.py")
        # Plumbing makes the base commit without running any commit hooks a machine adds.
        tree = self.git("write-tree")
        base = self.git("-c", "user.email=t@example.com", "-c", "user.name=t", "commit-tree", tree, "-m", "base")
        self.git("update-ref", "HEAD", base)

    def tearDown(self):
        self.scratch.cleanup()

    def run_main(self, *args):
        out = io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.repo)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                code = main(list(args))
        finally:
            os.chdir(cwd)
        return code, out.getvalue()

    def test_every_language_is_read_and_only_docs_data_and_binaries_are_not(self):
        names = '["sleep", "usleep", "nanosleep", "yield"]\n'
        for code in ("rate.zig", "rate.wombat", "bin/rate"):
            Path(self.repo, code).parent.mkdir(exist_ok=True)
            Path(self.repo, code).write_text(names)
        for skipped in ("README.md", "package-lock.json", "config.yaml", "ui.min.js"):
            Path(self.repo, skipped).write_text(names)
        Path(self.repo, "logo.bin").write_bytes(b"\x00" + names.encode())
        code, out = self.run_main(".")
        self.assertEqual(code, 1)
        for read in ("rate.zig:1", "rate.wombat:1", "bin/rate:1"):
            self.assertIn(read, out)
        for skipped in ("README.md", "package-lock.json", "config.yaml", "ui.min.js", "logo.bin"):
            self.assertNotIn(skipped, out)

    def test_a_path_with_no_readable_source_is_unreadable_not_clean(self):
        Path(self.repo, "notes").mkdir()
        Path(self.repo, "notes", "plan.txt").write_text('["a1", "b2", "c3", "d4"]\n')
        code, out = self.run_main("notes", "missing")
        self.assertEqual(code, 2)
        self.assertIn("notes: 1 file, none read (prose .txt: 1)", out)
        self.assertIn("missing: matches no file", out)
        self.assertNotIn("No unsettled leads", out)

    def test_a_path_holding_only_tests_names_the_flag(self):
        Path(self.repo, "test_rule.py").write_text('X = ["a1", "b2", "c3", "d4"]\n')
        code, out = self.run_main("test_rule.py")
        self.assertEqual(code, 2)
        self.assertIn("test_rule.py: 1 file, none read (test files: 1; pass --include-tests)", out)

    def test_only_added_lines_are_reviewed(self):
        self.assertEqual(self.run_main("--since", "HEAD", "rule.py")[0], 0)
        with open(Path(self.repo, "rule.py"), "a") as f:
            f.write('NEW = ["e5", "f6", "g7", "h8"]\n')
        code, out = self.run_main("--since", "HEAD", "rule.py")
        self.assertEqual(code, 1)
        self.assertIn("rule.py:2", out)
        self.assertNotIn("rule.py:1 ", out)

    def test_a_complete_record_passes_the_census(self):
        Path(self.repo, "census.tsv").write_text(
            HEADER + "\nrule.py\tletters\tsample names\tnot-data\t-\t-\t-\tone fixture\n")
        self.assertEqual(self.run_main("--record", "census.tsv", "rule.py")[0], 0)
        self.assertEqual(self.run_main("rule.py")[0], 1)


if __name__ == "__main__":
    unittest.main()
