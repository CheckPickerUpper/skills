# Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

| Skill | The problem it fixes | Example |
|---|---|---|
| [antimatter-code-quality-review](./antimatter-code-quality-review/SKILL.md) | Reviews pad the list with style nitpicks and inflated severities, and miss a change that adds a second way to do something the code already does. Every finding here must survive an attempt to disprove it and come with a before-and-after. | `/antimatter-code-quality-review the staged changes` |
| [antimatter-codebase-structure-review](./antimatter-codebase-structure-review/SKILL.md) | Folders and modules drift into a shape nobody chose, and it is only noticed once a reorganization is expensive. | `/antimatter-codebase-structure-review src/billing` |
| [explain-diff](./explain-diff/SKILL.md) | You are reviewing or have merged a change you do not really understand. It writes a page with a walkthrough in execution order, what could break and a quiz. Based on [Geoffrey Litt's explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524). | `/explain-diff HEAD~3..HEAD` |
| [facts-as-data](./facts-as-data/SKILL.md) | The same list of names is copied across files, so a case missing from one copy breaks one check silently. It moves the list into one table with a check that fails on a missing case. | `/facts-as-data sweep src/rules` |
| [pizza1](./pizza1/SKILL.md) | An agent defends a choice with "it's what the codebase does" or "smallest fix" instead of whether it is correct. | `/pizza1 why keep status as a string?` |
| [readonly](./readonly/SKILL.md) | You ask a question and the agent starts changing code, or answers with "probably". It answers from evidence and changes nothing. | `why does login retry twice? /readonly` |
| [test-hygiene](./test-hygiene/SKILL.md) | Tests pass when nothing was checked, or check what another test already checks. It breaks each rule on purpose to see which tests fail. | `/test-hygiene review the tests in this diff` |
| [zen-of-checkpickerupper](./zen-of-checkpickerupper/SKILL.md) | Two designs both look fine and the choice comes down to taste. Twenty-one short principles settle it. | `/zen-of-checkpickerupper store the total or compute it?` |

Every skill also loads on its own when its situation comes up, except `readonly`, which you add to a question yourself.
