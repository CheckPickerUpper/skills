"""Tests of how blockers.py reads and rewrites the Blocked by record.

The bodies are the three line shapes real issues use. GitHub itself is
exercised by running `check` against a live repository.
"""

import unittest

import blockers as b

HOME = "example/app"
TITLED = (
    "- #1913 [Keep saved drafts when the session expires]"
    "(https://github.com/example/app/issues/1913): cannot prove the"
    " draft restore until the session refresh lands."
)
LINK_ONLY = (
    "- [Refresh expired sessions](https://github.com/example/app/issues/1918):"
    " the token store must keep the refresh token first."
)
PLAIN = "- #1900 Session token store: the server requires the store's schema."
BODY = f"## Outcome\n\nDrafts survive an expired session.\n\n## Blocked by\n\n{TITLED}\n\n## Done when\n\n- the draft restores\n"


def issue(body, *links):
    return {
        "number": 1791,
        "body": body,
        "repository": {"nameWithOwner": HOME},
        "blockedBy": {"nodes": [
            {"number": n, "state": state, "repository": {"nameWithOwner": HOME}}
            for n, state in links
        ]},
    }


class ReadingTheRecord(unittest.TestCase):
    def test_every_real_line_shape_yields_its_blocker_and_reason(self):
        body = f"## Blocked by\n\n{TITLED}\n{LINK_ONLY}\n{PLAIN}\n"
        lines = b.blocked_by_lines(body, HOME)
        self.assertEqual(lines[b.Ref(HOME, 1913)][:20], "cannot prove the dra")
        self.assertEqual(lines[b.Ref(HOME, 1918)][:20], "the token store must")
        self.assertEqual(lines[b.Ref(HOME, 1900)], "the server requires the store's schema.")

    def test_a_colon_in_the_title_stays_out_of_the_reason(self):
        line = "- #1921 [Sessions: refresh tokens](https://github.com/example/app/issues/1921): no export yet"
        self.assertEqual(b.blocked_by_lines("## Blocked by\n\n" + line, HOME)[b.Ref(HOME, 1921)], "no export yet")

    def test_every_reference_form_names_the_same_blocker(self):
        refs = {b.parse_ref(text, HOME) for text in (
            "1913", "#1913", "example/app#1913",
            "https://github.com/example/app/issues/1913")}
        self.assertEqual(refs, {b.Ref(HOME, 1913)})

    def test_references_outside_the_section_are_not_blockers(self):
        body = "## Outcome\n\n- #1913: mentioned here\n\n## Blocked by\n\n" + PLAIN + "\n"
        self.assertEqual(set(b.blocked_by_lines(body, HOME)), {b.Ref(HOME, 1900)})


class Findings(unittest.TestCase):
    def kinds(self, body, *links):
        return [kind for kind, _ in b.findings_for(issue(body, *links))]

    def test_a_link_with_its_reason_is_settled(self):
        self.assertEqual(self.kinds(BODY, (1913, "OPEN")), [])

    def test_a_link_without_a_reason_line_is_unsettled(self):
        self.assertEqual(self.kinds("## Outcome\n\nx\n", (1913, "OPEN")), ["unsettled"])

    def test_a_reason_line_without_a_link_is_unlinked(self):
        self.assertEqual(self.kinds(BODY), ["unlinked"])

    def test_a_line_with_no_reason_is_refused(self):
        self.assertEqual(self.kinds("## Blocked by\n\n- #1913\n", (1913, "OPEN")), ["no-reason"])

    def test_a_closed_blocker_has_landed(self):
        self.assertEqual(self.kinds(BODY, (1913, "CLOSED")), ["landed"])


class RewritingTheRecord(unittest.TestCase):
    def test_keep_adds_a_section_at_the_end_and_leaves_the_rest(self):
        body = "## Outcome\n\nDrafts survive an expired session.\n"
        updated = b.with_line(body, b.Ref(HOME, 1900), PLAIN, HOME)
        self.assertEqual(updated, body + "\n## Blocked by\n\n" + PLAIN + "\n")

    def test_keep_replaces_the_line_for_the_same_blocker(self):
        new = "- #1913 [Keep shell redirections](https://github.com/x/y/issues/1913): new reason"
        updated = b.with_line(BODY, b.Ref(HOME, 1913), new, HOME)
        self.assertEqual(updated, BODY.replace(TITLED, new))

    def test_keep_adds_a_second_blocker_inside_the_section(self):
        updated = b.with_line(BODY, b.Ref(HOME, 1900), PLAIN, HOME)
        self.assertEqual(updated, BODY.replace(TITLED, TITLED + "\n" + PLAIN))

    def test_drop_removes_the_line_and_the_empty_section(self):
        updated = b.without_line(BODY, b.Ref(HOME, 1913), HOME)
        self.assertEqual(updated, "## Outcome\n\nDrafts survive an expired session.\n\n## Done when\n\n- the draft restores\n")

    def test_drop_keeps_the_other_blockers(self):
        body = BODY.replace(TITLED, TITLED + "\n" + PLAIN)
        self.assertEqual(b.without_line(body, b.Ref(HOME, 1913), HOME), BODY.replace(TITLED, PLAIN))


if __name__ == "__main__":
    unittest.main()
