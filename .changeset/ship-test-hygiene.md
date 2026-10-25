---
"checkpickerupper-skills": minor
---

Ship **`test-hygiene`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`test-hygiene` (model-invoked) holds every test to two facts: it fails when its rule breaks, and no other test already fails for that break. Both are proved by breaking the rule on purpose and recording which tests fail. A test that cannot fail is fixed at its cause, usually code that collapses different failures into one answer; a test another test already catches is deleted; and a new test is written only when nothing existing fails for its break.
