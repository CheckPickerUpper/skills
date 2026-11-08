---
"checkpickerupper-skills": minor
---

**`zen-of-checkpickerupper`** grows to twenty-three lines and cites only published skills.

Two new lines judge how a value moves through code: "Decide once; downstream takes the piece, not the whole" (branch on the case at one boundary and pass the narrower piece, so a case without it cannot be passed in) and "Return the thing, not whether you have it" (a yes/no that guards data it does not hold can disagree with it). Line 1 now gives the test for placing a field: does it mean something for every case, or is a value on the wrong case nonsense. Line 6 adds two duplicate-owner examples: two accessors answering "has it" for the same cases, and one value reachable through two fields.

- Each expansion now names `correct-by-construction` or `antimatter-code-quality-review` as its source instead of skills that were never published.
