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

### Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

- **[antimatter-code-quality-review](./skills/engineering/antimatter-code-quality-review/SKILL.md)** — Deep code-quality and pre-merge review of a commit, PR, branch, or diff. Audit correctness, intent, naming, cohesion, types, boundaries, control flow, duplication, cost, allocation, and generalization. Check predictability: does a feature or fix create a second way to perform a capability the codebase already has? Compare existing implementations, reuse or extend sound patterns, and extract shared behavior without letting one feature own the abstraction or inventing flexibility. Every finding needs evidence, a concrete before-and-after, behavior preservation, and adversarial refutation.
- **[antimatter-codebase-structure-review](./skills/engineering/antimatter-codebase-structure-review/SKILL.md)** — Audits hierarchy, naming, ownership, dependency boundaries, and growth readiness; every finding must survive refutation and specify an evidence-backed change.
- **[explain-diff](./skills/engineering/explain-diff/SKILL.md)** — Explain a code change, diff, branch, or PR as a self-contained page: background, intuition with a worked example, a walkthrough in execution order, what could break, and a quiz a script shuffles and audits so the longest answer never gives it away. HTML or Markdown; `--quiz chat` asks free-response questions instead. Based on [Geoffrey Litt's explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524); [what we changed and why](./skills/engineering/explain-diff/README.md).
- **[facts-as-data](./skills/engineering/facts-as-data/SKILL.md)** — Move a fact buried in logic (a hard-coded name list, a regex of names, branches that differ only in data) into one table every reader shares, before a second copy exists. A script finds the leads and checks the census; each table gets a key, storage that merges, its readers and a check that fails on a missing case; code with no real axis of variation stays code.
- **[pizza1](./skills/engineering/pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, transition size, compatibility, legacy paths, or scope.
- **[readonly](./skills/engineering/readonly/SKILL.md)** — Prove, don't guess. A user-invoked modifier for codebase questions and other skills: exhaust read-only evidence, avoid "likely" answers when facts can be checked, and stop before implementation, issues, commits, or remote changes.
- **[test-hygiene](./skills/engineering/test-hygiene/SKILL.md)** — Every test must fail when its rule breaks, and be the only test that does. Proves both by breaking the rule on purpose: a test that still passes is fixed with the code that hid the failure, and a test another test already catches is deleted.
- **[zen-of-checkpickerupper](./skills/engineering/zen-of-checkpickerupper/SKILL.md)** — The Zen of CheckPickerUpper: twenty-one lines that judge designs, fixes, abstractions, types, structure, and questions, each expanded and traced to its source skill. Use when settling a design choice or an ambiguous question, choosing between options, judging whether a fix, abstraction, type, or layout is right, or when someone asks for the zen of checkpickerupper.

### Productivity

General workflow tools.

- **[audit-issues](./skills/productivity/audit-issues/SKILL.md)** — Audit a GitHub tracker into one issue per cause: a script finds open work hidden under closed issues, suggests likely slices of one cause and milestones over 10 causes, and flags workaround premises; every open issue gets a checked verdict (done, duplicate, slice, cause, wrong premise, out of date, still real, or unsure with why its check cannot run); the owner approves a short before-and-after page before the script applies it. Its draft check stops to-issues-clearly filing what an audit would undo.
- **[check-protection](./skills/productivity/check-protection/SKILL.md)** — Before an expensive or repeated check, name the wrong behaviour it catches and what cheaper evidence already covers. Keep required gates, reuse valid results, and audit every nested step. A script validates the recorded audit decisions.
- **[close-issues](./skills/productivity/close-issues/SKILL.md)** — Close GitHub issues only with proof: a script refuses a close while sub-issues or checklist lines are open, and records the proof, a duplicate's carried details or the owner's not-planned decision in the body. Use whenever an issue is about to close.
- **[compose-goal](./skills/productivity/compose-goal/SKILL.md)** — Compose or retrieve a gist-backed agent goal with a human outcome, live issue references, traceable implementation scope, and real behavior proof.
- **[dependency-trace](./skills/productivity/dependency-trace/SKILL.md)** — Derive a correctness dependency graph before implementation. Use when determining foundations, dependency order, or a lowest-to-highest flow for a feature.
- **[make-diagram](./skills/productivity/make-diagram/SKILL.md)** — Draw any diagram (system map, flowchart, pipeline, process map) a stranger can read: settle the domain and the owner's words first, show the mechanism as nodes, yes/no diamonds and one lane per source of truth, with semantic arrow colours and nothing floating. A script renders light and dark images and refuses overlaps, small text, crammed boxes, unlabelled branches, backward or crossing arrows and captions.
- **[settle-blockers](./skills/productivity/settle-blockers/SKILL.md)** — Decide whether each blocked-by link between issues is real: blocked only when the work cannot be done now or doing it now means redoing it, never for a shared file or a merge conflict. Unclear links go to cheap subagents in parallel. A script keeps each real link paired with a reason line under `## Blocked by` and removes the rest.
- **[to-issues-clearly](./skills/productivity/to-issues-clearly/SKILL.md)** — Create GitHub issues whose titles a stranger can act on. Refuses rhetoric, sarcasm, personified code, and type vocabulary dressed as domain language; splits issues by whether anything visibly breaks; makes each issue one cause with one fix and adds new sightings to the existing issue, demands watchable acceptance criteria, and labels by issue kind with bug priority; wires real sub-issue, blocked-by, and duplicate edges rather than prose references; offers an existing or new milestone when the issues serve one deliverable and flags catch-all milestones. Use when turning a plan, audit or bug report into tracked work.
- **[issues-to-outcomes](./skills/productivity/issues-to-outcomes/SKILL.md)** — Report finished work as what the reader would notice instead of a list of issue and PR titles: how much of it shows in the product, each visible change as before and now, and the invisible work as what was stuck and no longer is. A script refuses a draft whose lines open with a tracker reference. Use for status updates, day or session summaries, and handoffs.

### Misc

Tools kept around but rarely used. None yet.

## Local Development

```bash
./scripts/list-skills.sh
./scripts/list-skills.sh --client codex
./scripts/link-skills.sh --client claude
./scripts/link-skills.sh --client codex
./scripts/link-skills.sh --client gemini
./scripts/link-skills.sh --client pi
./scripts/link-skills-all.sh
# Replace stale real copies with links to this repo, keeping recoverable backups.
./scripts/link-skills-all.sh --replace-existing
```

## Client targeting

Skills are universal by default. Add an explicit allow-list only when a skill
depends on one client's tools or runtime:

```yaml
name: codex-only-workflow
description: Run a workflow that requires Codex-only capabilities.
clients: [codex]
```

The registered client names are `claude`, `codex`, `gemini`, `antigravity`,
`antigravity-cli`, and `pi`. Use a list when a skill supports more than one
client, for example `clients: [claude, codex]`. An omitted `clients` field
means every registered client. The registry lives in
`scripts/agent-targets.json`, so adding a client does not require changing the
metadata parser or linker. The linker validates unknown names and removes an
old symlink from a client when a skill no longer targets it. Skill instructions
remain one shared body; only discovery and delivery are client-specific.

The default destinations are `~/.claude/skills`, `~/.agents/skills`,
`~/.gemini/skills`, `~/.gemini/config/skills`,
`~/.gemini/antigravity-cli/skills`, and `~/.pi/agent/skills`. Set the
destination environment variable named for the client in
`scripts/agent-targets.json` when a client uses a different destination.

The `clients` field is enforced by this repository's list and link scripts.
Other installers must apply the same filter before adding a skill to their
catalog; metadata alone cannot stop a client that ignores it from loading the
file. Keep every published skill in the README catalogs, but add a
client-targeted skill to `.claude-plugin/plugin.json` only when it targets
Claude or is universal.

## Publishing

Publish skills, catalog entries, and plugin registrations directly to `main`
from a task worktree after validation. Routine releases do not use GitHub issues
or pull requests. If GitHub rejects a direct push, report the exact restriction
instead of routing the change through an issue or pull request.

Every pushed change to a published skill, catalog entry, or plugin
registration carries a changeset: run `npx changeset`, choose the bump
(`major` for a removed or renamed skill or a breaking contract, `minor` for a
new skill, `patch` for a fix or wording change), and describe what changed for
someone who uses the skill. Commit the generated `.changeset/*.md` with the
change.

Write one changeset per change, in the shape of the existing entries in
`CHANGELOG.md`:

- Open with one sentence naming what changed, with the skill in bold code,
  such as "Ship **`pizza1`** in the **Engineering** bucket, so it installs
  with `npx skills` and loads from the Claude Code plugin."
- Follow with a paragraph that names the skill, marks it `(user-invoked)` or
  `(model-invoked)`, and says what it now does for its user.
- Add bullets only for distinct behavior changes, and an upgrade step only
  when users must act.

## Releases

Pending changesets on `main` become a release when you run:

```bash
npm ci
npm run release
```

This starts the Release workflow, waits for it, and prints the release page.
The workflow consumes the changesets into `CHANGELOG.md`, bumps the version in
`package.json` and `.claude-plugin/plugin.json`, commits
`chore: version skills vX.Y.Z` to `main`, and publishes the
[GitHub Release](https://github.com/CheckPickerUpper/skills/releases) `vX.Y.Z`
with that version's changelog as its notes. Pull `main` afterwards. With no
pending changesets, the workflow fails without changing anything.
