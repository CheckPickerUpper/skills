"""Tests of the release notes written from a changelog section and the README catalog."""

import unittest

from release_notes import notes

README = """| Skill | The problem it fixes | Example |
|---|---|---|
| [alpha](./skills/engineering/alpha/SKILL.md) | Alpha's problem stated plainly. A second sentence. | `/alpha` |
| [beta](./skills/productivity/beta/SKILL.md) | Beta's problem. | `/beta` |
"""

CHANGELOG = """# pkg

## 2.0.0

### Major Changes

- [`aaaaaaa`](https://example.com/c/a) Remove **`gamma`** from the bucket.

### Minor Changes

- [`bbbbbbb`](https://example.com/c/b) Thanks [@someone](https://example.com/someone)! - Ship **`alpha`** in the bucket.

  Its longer description.

### Patch Changes

- [`ccccccc`](https://example.com/c/c) beta: a fix.
- [`ddddddd`](https://example.com/c/d) Reconcile stale skill links before installing.

## 1.0.0

### Major Changes

- [`eeeeeee`](https://example.com/c/e) Ship **`beta`** in the bucket.
"""


class ReleaseNotes(unittest.TestCase):
    def setUp(self):
        self.text = notes("2.0.0", CHANGELOG, README)
        self.summary, self.detail = self.text.split("## Nitty-gritty")

    def test_a_new_skill_is_listed_with_its_whole_catalog_use_it_when_cell(self):
        self.assertIn("| **alpha** | Alpha's problem stated plainly. A second sentence. |", self.summary)
        self.assertNotIn("**beta** |", self.summary)

    def test_retired_improved_and_repository_changes_each_get_their_own_line(self):
        self.assertIn("**Retired:** gamma.", self.summary)
        self.assertIn("**Improved:** beta.", self.summary)
        self.assertIn("**Repository:** 1 change", self.summary)

    def test_the_full_section_follows_under_nitty_gritty_without_the_next_version(self):
        self.assertIn("#### Minor Changes", self.detail)
        self.assertIn("Its longer description.", self.detail)
        self.assertNotIn("eeeeeee", self.detail)

    def test_a_missing_version_stops_with_its_name(self):
        with self.assertRaisesRegex(SystemExit, "3.0.0"):
            notes("3.0.0", CHANGELOG, README)


if __name__ == "__main__":
    unittest.main()
