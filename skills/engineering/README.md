# Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

| Skill | Use it when | Example |
|---|---|---|
| [antimatter-code-quality-review](./antimatter-code-quality-review/SKILL.md) | Before you merge a change, to get a review that reports only real problems, each with proof and a before-and-after. | `/antimatter-code-quality-review the staged changes` |
| [antimatter-codebase-structure-review](./antimatter-codebase-structure-review/SKILL.md) | Before reorganizing folders or modules, or when a change might put code in the wrong place. | `/antimatter-codebase-structure-review src/billing` |
| [explain-diff](./explain-diff/SKILL.md) | You need to understand a change, branch or PR you did not write. It writes a page with a walkthrough, what could break and a quiz. Based on [Geoffrey Litt's explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524). | `/explain-diff HEAD~3..HEAD` |
| [facts-as-data](./facts-as-data/SKILL.md) | The same list of names (file types, commands, error codes) is copied in several places in your code, and adding one means finding every copy. | `/facts-as-data sweep src/rules` |
| [pizza1](./pizza1/SKILL.md) | An agent defends a choice with "it's what the codebase does" or "smallest fix", and you want the correct answer instead. | `/pizza1 why keep status as a string?` |
| [readonly](./readonly/SKILL.md) | You want an answer about your code, backed by evidence, without the agent changing anything. | `why does login retry twice? /readonly` |
| [test-hygiene](./test-hygiene/SKILL.md) | You are writing or reviewing tests and want each one to fail when its rule breaks, with no test repeating another. | `/test-hygiene review the tests in this diff` |
| [zen-of-checkpickerupper](./zen-of-checkpickerupper/SKILL.md) | You are choosing between two designs that both seem fine. | `/zen-of-checkpickerupper store the total or compute it?` |

Every skill also loads on its own when its situation comes up, except `readonly`, which you add to a question yourself.
