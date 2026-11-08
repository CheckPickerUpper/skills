# Skills

[![skills.sh](https://skills.sh/b/CheckPickerUpper/skills)](https://skills.sh/CheckPickerUpper/skills)

Agent skills for correctness-first engineering and clear technical judgment.

These skills are tailored toward real engineers, but still usable for vibe coders.

## Quickstart

```bash
npx skills@latest add CheckPickerUpper/skills
```

Install everything without prompts:

```bash
npx skills@latest add CheckPickerUpper/skills --all
```

Use one skill without installing:

```bash
npx skills@latest use CheckPickerUpper/skills@pizza1
```

## Reference

Every skill also loads on its own when its situation comes up, except `readonly`, which you add to a question yourself.

### Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

| Skill | Use it when | Example |
|---|---|---|
| [antimatter-code-quality-review](./skills/engineering/antimatter-code-quality-review/SKILL.md) | Before you merge a change, to get a review that reports only real problems, each with proof and a before-and-after. | `/antimatter-code-quality-review the staged changes` |
| [antimatter-codebase-structure-review](./skills/engineering/antimatter-codebase-structure-review/SKILL.md) | Before reorganizing folders or modules, or when a change might put code in the wrong place. | `/antimatter-codebase-structure-review src/billing` |
| [correct-by-construction](./skills/engineering/correct-by-construction/SKILL.md) | The same kind of bug keeps coming back in new forms, or the bug in front of you looks like a sign of a bigger problem somewhere else. You want that problem made impossible to write instead of patched again, including types that drift from their source and facts kept in two places. | `/correct-by-construction an order can ship before it is paid` |
| [explain-diff](./skills/engineering/explain-diff/SKILL.md) | You need to understand a change, branch or PR you did not write. It writes a page with a walkthrough, what could break and a quiz. Based on [Geoffrey Litt's explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524). | `/explain-diff HEAD~3..HEAD` |
| [facts-as-data](./skills/engineering/facts-as-data/SKILL.md) | The same list of names (file types, commands, error codes) is copied in several places in your code, and adding one means finding every copy. | `/facts-as-data sweep src/rules` |
| [pizza1](./skills/engineering/pizza1/SKILL.md) | An agent defends a choice with "it's what the codebase does" or "smallest fix", and you want the correct answer instead. | `/pizza1 why keep status as a string?` |
| [readonly](./skills/engineering/readonly/SKILL.md) | You want an answer about your code, backed by evidence, without the agent changing anything. | `why does login retry twice? /readonly` |
| [ruthless-bottleneck-destroyer](./skills/engineering/ruthless-bottleneck-destroyer/SKILL.md) | Your tests or CI take too long, or you are writing tests and want each one to catch its bug, with no test repeating another and none slower than it needs to be. Checks that guard code nothing uses, or a mistake a type or import could rule out, get deleted. It keeps going until every test is under the time limit you set. | `/ruthless-bottleneck-destroyer every test under 1 second` |
| [zen-of-checkpickerupper](./skills/engineering/zen-of-checkpickerupper/SKILL.md) | You are choosing between two designs that both seem fine. | `/zen-of-checkpickerupper store the total or compute it?` |

### Productivity

General workflow tools.

| Skill | Use it when | Example |
|---|---|---|
| [anti-ai-slop-writing](./skills/productivity/anti-ai-slop-writing/SKILL.md) | You are having an agent write a web page, article, email or document, and you don't want it to read like a chatbot wrote it. It also bans lists of three. | `/anti-ai-slop-writing write the About page for our bakery` |
| [audit-issues](./skills/productivity/audit-issues/SKILL.md) | Your GitHub repository has so many open issues that you cannot tell which are duplicates, already done, or still need work. | `/audit-issues OWNER/REPO` |
| [close-issues](./skills/productivity/close-issues/SKILL.md) | An agent is about to close a GitHub issue. It refuses until every sub-issue and checklist item is done, counts a checklist item done only when a landed commit names it, and writes the proof into the issue. | `/close-issues #142 is finished` |
| [compose-goal](./skills/productivity/compose-goal/SKILL.md) | You are handing a task to another agent and want it to get the outcome, the issue links and how to prove it works. | `/compose-goal hand #142 to another agent` |
| [cut-extraneous-load](./skills/productivity/cut-extraneous-load/SKILL.md) | Your agent's replies are pretentious and long-winded, and you want only what you need to know. Especially useful at the end of a long day, when your brain hurts. | `/cut-extraneous-load say that again without the filler` |
| [dependency-trace](./skills/productivity/dependency-trace/SKILL.md) | Before building a feature, to work out what has to exist first and in what order. | `/dependency-trace what does checkout depend on?` |
| [issues-to-outcomes](./skills/productivity/issues-to-outcomes/SKILL.md) | You are writing a status update or end-of-day summary and want it to say what changed for the reader, not list issue titles. | `/issues-to-outcomes what landed this week` |
| [make-diagram](./skills/productivity/make-diagram/SKILL.md) | You need a diagram (flowchart, system map, pipeline) that someone new can read. | `/make-diagram how a payment goes from cart to receipt` |
| [settle-blockers](./skills/productivity/settle-blockers/SKILL.md) | An issue is marked as blocked by another issue and you want to know whether it really has to wait. | `/settle-blockers OWNER/REPO#88` |
| [to-issues-clearly](./skills/productivity/to-issues-clearly/SKILL.md) | You are turning a plan, bug report or audit into GitHub issues and want titles you can understand without opening them. | `/to-issues-clearly turn this plan into issues` |

## Updates

Each release's notes, new skills first, are on the
[Releases page](https://github.com/CheckPickerUpper/skills/releases).

To work on the skills themselves, see [CONTRIBUTING.md](./CONTRIBUTING.md).
