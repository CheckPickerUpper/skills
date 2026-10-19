"""Behavioral tests of check_diagram.py at its command line, in a real browser.

Each case breaks one rule in the reference example and expects the checker to
name it. Run with: python3 -m unittest test_check_diagram (needs uv and Chrome
or Playwright's Chromium).
"""

from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "check_diagram.py"
EXAMPLE = (HERE.parent / "references" / "example.svg").read_text()

NO_ARROW = '<path class="arrow no" d="M700 415 V488" marker-end="url(#head-no)"/>'
NO_LABEL = '<text class="label" x="712" y="458">no</text>'
YES_LABEL = '<text class="label" x="889" y="328" text-anchor="middle">yes</text>'
FIRST_DATA = '<path class="arrow data" d="M250 110 H328" marker-end="url(#head-data)"/>'
LEGEND_START = '<g class="legend">'
SETTLE_NODE = ('<g class="node">\n'
               '    <rect x="960" y="300" width="190" height="80" rx="10" fill="#d6f2e0"/>\n'
               '    <text x="1055" y="334" text-anchor="middle" class="title">Settle the bet</text>\n'
               '    <text x="1055" y="356" text-anchor="middle">winners paid that day</text>\n'
               '  </g>')
REFUND_EXAMPLE = '\n    <text x="700" y="546" text-anchor="middle">e.g. no clip of the jumper</text>'
CROSSING = ('arrow "Copy official stats" → "Settle the bet" crosses'
            ' the arrow "League box score" → "Settle the bet"')


def replaced(old, new, text=EXAMPLE):
    if old not in text:
        raise AssertionError(f"fixture text not found: {old}")
    return text.replace(old, new)


def before_legend(markup):
    return replaced(LEGEND_START, markup + "\n  " + LEGEND_START)


class CheckDiagram(unittest.TestCase):
    def run_check(self, content, name="diagram.svg", words="", accepted=None):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / name
            path.write_text(content)
            if words is not None:
                path.with_suffix(".words.txt").write_text(words)
            if accepted is not None:
                path.with_suffix(".accepted.txt").write_text(accepted)
            result = subprocess.run(
                ["uv", "run", "--quiet", str(SCRIPT), str(path)],
                capture_output=True, text=True, timeout=180,
            )
            images = sorted(p.name for p in Path(folder).glob("*.png"))
        return result, images

    def assert_finding(self, content, *expected, **options):
        result, _ = self.run_check(content, **options)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for text in expected:
            self.assertIn(text, result.stdout)

    def test_the_example_passes_and_renders_both_themes(self):
        result, images = self.run_check(EXAMPLE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(images, ["diagram.dark.png", "diagram.light.png"])

    def test_small_text_is_refused(self):
        self.assert_finding(
            replaced("font-size: 15px", "font-size: 12px"),
            '"the final score" is 12.0px where it is drawn',
            "Text is 15px or larger")

    def test_label_on_its_line_is_refused(self):
        self.assert_finding(
            replaced(YES_LABEL, YES_LABEL.replace('y="328"', 'y="346"')),
            '"yes" sits on the arrow "Proof clip found" → "Settle the bet"')

    def test_paragraph_in_a_box_is_refused(self):
        self.assert_finding(
            replaced('<text x="150" y="345" text-anchor="middle" class="title">Game video</text>',
                     '<text x="150" y="322" text-anchor="middle" class="title">Game video</text>'
                     '<text x="150" y="340" text-anchor="middle">broadcast feed</text>'
                     '<text x="150" y="358" text-anchor="middle">every camera angle</text>'
                     '<text x="150" y="376" text-anchor="middle">kept for the season</text>'),
            'node "Game video" has 4 rows of text')

    def test_a_titled_checklist_box_passes(self):
        result, _ = self.run_check(replaced(
            SETTLE_NODE,
            '<g class="node">\n'
            '    <rect x="960" y="300" width="190" height="230" rx="10" fill="#d6f2e0"/>\n'
            '    <text x="1055" y="334" text-anchor="middle" class="title">Settle the bet</text>\n'
            '    <text x="975" y="358">Paid out:</text>\n'
            '    <text x="985" y="380">• winners that day</text>\n'
            '    <text x="985" y="402">• refunds by 6pm</text>\n'
            '    <text x="975" y="426">Sent:</text>\n'
            '    <text x="985" y="448">• a receipt per bet</text>\n'
            '    <text x="985" y="470">• the clip as proof</text>\n'
            '  </g>'))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_vague_and_row_is_refused(self):
        self.assert_finding(
            replaced(">winners paid that day<", ">jerseys and the court<"),
            'node "Settle the bet" joins two things with "and": "jerseys and the court"')

    def test_a_check_with_no_real_example_is_refused(self):
        self.assert_finding(
            replaced(REFUND_EXAMPLE, ""),
            'decision "Proof clip found" shows no real example')

    def test_long_row_that_spills_is_refused(self):
        self.assert_finding(
            replaced(">the final score<", ">the final official box score feed<"),
            'has a 33-character row',
            'spills out of node "League box score"')

    def test_unconnected_node_and_loose_note_are_refused(self):
        self.assert_finding(
            before_legend(
                '<g class="node"><rect x="960" y="70" width="190" height="80" rx="10" fill="#dbeafe"/>'
                '<text x="1055" y="115" text-anchor="middle" class="title">Pay sportsbook</text></g>'
                '<text class="label" x="40" y="690">Note: refunds take a day</text>'),
            'node "Pay sportsbook" has no arrow to or from it',
            '"Note: refunds take a day" is loose text that labels no arrow')

    def test_decision_without_a_no_branch_is_refused(self):
        self.assert_finding(
            replaced(NO_LABEL, "", replaced(NO_ARROW, "")),
            'decision "Proof clip found" is missing its no branch',
            'the legend shows a no arrow the diagram does not use')

    def test_unlabelled_branch_is_refused(self):
        self.assert_finding(
            replaced(NO_LABEL, ""),
            'the no branch of decision "Proof clip found" has no label')

    def test_backward_arrow_is_refused(self):
        self.assert_finding(
            replaced(FIRST_DATA, FIRST_DATA.replace("M250 110 H328", "M328 110 H252")),
            'arrow "Copy official stats" → "League box score" points right to left within a row')

    def test_crossing_arrows_are_refused(self):
        self.assert_finding(
            before_legend('<path class="arrow data" d="M150 150 V200 H1100 V298"/>'),
            CROSSING)

    def test_a_crossing_accepted_with_a_reason_passes(self):
        result, _ = self.run_check(
            before_legend('<path class="arrow data" d="M150 150 V200 H1100 V298"/>'),
            accepted=CROSSING + " | both lanes must reach the settle box\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("accepted judgment call: " + CROSSING, result.stdout)

    def test_a_crossing_accepted_without_a_reason_is_refused(self):
        self.assert_finding(
            before_legend('<path class="arrow data" d="M150 150 V200 H1100 V298"/>'),
            "without a reason", accepted=CROSSING + "\n")

    def test_a_hard_finding_cannot_be_accepted(self):
        moved = replaced(YES_LABEL, YES_LABEL.replace('y="328"', 'y="346"'))
        sits = '"yes" sits on the arrow "Proof clip found" → "Settle the bet"'
        self.assert_finding(moved, "\n  - " + sits + "\n", accepted=sits + " | looks fine to me\n")

    def test_a_stale_accepted_line_is_refused(self):
        self.assert_finding(
            EXAMPLE, "which is not a current judgment finding",
            accepted=CROSSING + " | from an earlier layout\n")

    def test_arrow_through_a_box_is_refused(self):
        self.assert_finding(
            before_legend('<path class="arrow data" d="M50 340 H30 V530 H598"/>'),
            'runs through node "Label the miss"')

    def test_wrong_colour_and_missing_legend_are_refused(self):
        recoloured = replaced(".yes { stroke: #2e9e5b; }", ".yes { stroke: #2f6fd6; }")
        start = recoloured.index(LEGEND_START)
        end = recoloured.index("</g>", start) + len("</g>")
        self.assert_finding(
            recoloured[:start] + recoloured[end:],
            "is a yes arrow but is not green",
            "and has no legend")

    def test_solid_loop_is_refused(self):
        self.assert_finding(
            replaced("stroke-dasharray: 8 6;", ""),
            "is a loop arrow but is solid, not dashed")

    def test_caption_is_refused(self):
        page = ("<!doctype html><html><body><figure>" + EXAMPLE
                + "<figcaption>What changed: refunds now retrain.</figcaption></figure></body></html>")
        self.assert_finding(page, "the figure has a <figcaption>", name="page.html")

    def test_light_text_in_the_dark_theme_is_refused(self):
        self.assert_finding(
            replaced(".lane > text, .label, .legend text { fill: #e6edf3; }",
                     ".lane > text, .label, .legend text, .node text { fill: #e6edf3; }"),
            'dark theme: "Game video" has contrast',
            "light text on a darker fill")

    def test_corrected_words_are_refused(self):
        self.assert_finding(
            EXAMPLE,
            '"League box score" uses "box score"; write "official stats"',
            words="# owner, 2026-10-14\nbox score => official stats\n")

    def test_a_corrected_word_inside_a_longer_word_passes(self):
        result, _ = self.run_check(EXAMPLE, words="win =>\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_comma_list_in_a_box_is_refused(self):
        self.assert_finding(
            replaced(">no AI touches them<", ">points, rebounds, assists<"),
            'node "Copy official stats" lists items with commas: "points, rebounds, assists"')

    def test_a_step_drawn_in_both_lanes_is_refused(self):
        self.assert_finding(
            replaced(">Label the miss<", ">Settle the bet<"),
            '"Settle the bet" is drawn 2 times')

    def test_an_end_with_only_its_name_is_refused(self):
        self.assert_finding(
            replaced('\n    <text x="1055" y="356" text-anchor="middle">winners paid that day</text>', ""),
            'end "Settle the bet" says only its name')

    def test_a_diagram_without_a_words_file_is_refused(self):
        self.assert_finding(EXAMPLE, "diagram.words.txt does not exist", words=None)

    def test_a_page_without_the_vocabulary_is_refused(self):
        self.assert_finding(
            "<!doctype html><svg><rect width='10' height='10'/></svg>",
            "no diagram found", name="page.html")

    def test_a_missing_file_is_unusable(self):
        result = subprocess.run(
            ["uv", "run", "--quiet", str(SCRIPT), "/nonexistent/diagram.svg"],
            capture_output=True, text=True, timeout=180,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
