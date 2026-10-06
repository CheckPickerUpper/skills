---
"checkpickerupper-skills": minor
---

Ship **`explain-diff`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`explain-diff` (model-invoked) turns a change, diff, branch or PR into one self-contained page: background, intuition with a worked example, a walkthrough in the order the code runs with `path:line` links, what could break, and a quiz. It is based on Geoffrey Litt's `explain-diff` gist and fixes what that gist's readers reported:

- The quiz is written as data and a script places the answers, so the right one is not in a predictable spot, and the build refuses a quiz whose correct answers are noticeably the longest.
- `--quiz chat` replaces multiple choice with free-response questions graded in the conversation.
- The diff and PR text are treated as data, never instructions.
- A fixed template carries all CSS and JavaScript, so each run spends its tokens on the explanation; `--md` writes plain Markdown for the lowest cost.
