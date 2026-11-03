# Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

| Skill | Use it when | Example |
|---|---|---|
| [antimatter-code-quality-review](./antimatter-code-quality-review/SKILL.md) | Before you merge a change, to get a review that reports only real problems, each with proof and a before-and-after. | `/antimatter-code-quality-review the staged changes` |
| [antimatter-codebase-structure-review](./antimatter-codebase-structure-review/SKILL.md) | Before reorganizing folders or modules, or when a change might put code in the wrong place. | `/antimatter-codebase-structure-review src/billing` |
| [correct-by-construction](./correct-by-construction/SKILL.md) | The same kind of bug keeps coming back in new forms, or the bug in front of you looks like a sign of a bigger problem somewhere else. You want that problem made impossible to write instead of patched again, including types that drift from their source and facts kept in two places. | `/correct-by-construction an order can ship before it is paid` |
| [explain-diff](./explain-diff/SKILL.md) | You need to understand a change, branch or PR you did not write. It writes a page with a walkthrough, what could break and a quiz. Based on [Geoffrey Litt's explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524). | `/explain-diff HEAD~3..HEAD` |
| [facts-as-data](./facts-as-data/SKILL.md) | The same list of names (file types, commands, error codes) is copied in several places in your code, and adding one means finding every copy. | `/facts-as-data sweep src/rules` |
| [pizza1](./pizza1/SKILL.md) | An agent defends a choice with "it's what the codebase does" or "smallest fix", and you want the correct answer instead. | `/pizza1 why keep status as a string?` |
| [readonly](./readonly/SKILL.md) | You want an answer about your code, backed by evidence, without the agent changing anything. | `why does login retry twice? /readonly` |
| [ruthless-bottleneck-destroyer](./ruthless-bottleneck-destroyer/SKILL.md) | Your tests or CI take too long, or you are writing tests and want each one to catch its bug, with no test repeating another and none slower than it needs to be. Checks that guard code nothing uses, or a mistake a type or import could rule out, get deleted. It keeps going until every test is under the time limit you set. | `/ruthless-bottleneck-destroyer every test under 1 second` |
| [zen-of-checkpickerupper](./zen-of-checkpickerupper/SKILL.md) | You are choosing between two designs that both seem fine. | `/zen-of-checkpickerupper store the total or compute it?` |

Every skill also loads on its own when its situation comes up, except `readonly`, which you add to a question yourself.
