"""Exercise installed skill links against a real filesystem."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


class LinkSkills(unittest.TestCase):
    def test_given_renamed_and_deleted_sources_when_linking_then_remove_only_owned_stale_links(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            repo = root / "repo"
            scripts = repo / "scripts"
            scripts.mkdir(parents=True)
            for name in ("link-skills.sh", "skill-targets.py", "agent-targets.json"):
                (scripts / name).symlink_to(SCRIPTS / name)
            source = repo / "skills" / "published" / "original"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("---\nname: original\ndescription: Example\n---\n")
            deleted = source.with_name("deleted")
            deleted.mkdir()
            (deleted / "SKILL.md").write_text("---\nname: deleted\ndescription: Example\n---\n")
            dest = root / "installed"
            dest.mkdir()
            foreign = root / "foreign"
            foreign.mkdir()
            (dest / "foreign").symlink_to(foreign)
            (dest / "foreign-missing").symlink_to(root / "missing")
            (dest / "real-directory").mkdir()
            env = {**os.environ, "CODEX_SKILLS_DIR": str(dest)}

            def link():
                return subprocess.run(
                    [str(scripts / "link-skills.sh"), "--client", "codex"],
                    env=env, text=True, capture_output=True, check=False,
                )

            first = link()
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual((dest / "original").resolve(), source)
            renamed = source.with_name("renamed")
            source.rename(renamed)
            (deleted / "SKILL.md").unlink()
            deleted.rmdir()

            result = link()

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((dest / "original").is_symlink())
            self.assertFalse((dest / "deleted").is_symlink())
            self.assertEqual((dest / "renamed").resolve(), renamed)
            self.assertEqual((dest / "foreign").readlink(), foreign)
            self.assertEqual((dest / "foreign-missing").readlink(), root / "missing")
            self.assertTrue((dest / "real-directory").is_dir())


if __name__ == "__main__":
    unittest.main()
