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

- **[antimatter-code-quality-review](./skills/engineering/antimatter-code-quality-review/SKILL.md)** — Total annihilation: no finding survives unless it survives refutation. Inspired by Cursor's [Thermo-Nuclear review](https://github.com/cursor/plugins/blob/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md), [Matt Pocock's skills](https://github.com/mattpocock/skills), and correctness-first design philosophy; pins the diff frame, checks intent and repo standards, and only reports provable findings.
- **[code-review](./skills/engineering/code-review/SKILL.md)** — Review a fixed diff for documented standards and fit to its originating spec or ticket.
- **[implement](./skills/engineering/implement/SKILL.md)** — Implement an approved ticket slice, then hand it through TDD and review.
- **[pizza1](./skills/engineering/pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, transition size, compatibility, legacy paths, or scope.
- **[readonly](./skills/engineering/readonly/SKILL.md)** — Prove, don't guess. A user-invoked modifier for codebase questions and other skills: exhaust read-only evidence, avoid "likely" answers when facts can be checked, and stop before implementation, issues, commits, or remote changes.
- **[tdd](./skills/engineering/tdd/SKILL.md)** — Drive behavior through a red-green-refactor loop at an agreed public seam.
- **[to-spec](./skills/engineering/to-spec/SKILL.md)** — Turn aligned decisions into a durable feature spec.
- **[to-tickets](./skills/engineering/to-tickets/SKILL.md)** — Break a spec into vertical tickets with real blockers.

### Productivity

General workflow tools.

- **[grill-with-docs-requiem](./skills/productivity/grill-with-docs-requiem/SKILL.md)** — A design interview that asks useful batches, infers obvious answers, and records settled domain language and ADRs as the conversation progresses. Use when sharpening a plan while maintaining docs.
- **[grill-with-docs](./skills/productivity/grill-with-docs/SKILL.md)** — Align a fuzzy idea, settle the important decisions, and hand a bounded destination to the spec stage.
- **[skill-router](./skills/productivity/skill-router/SKILL.md)** — Choose one exact next skill from the generated catalog when the user's intent is not already named.
- **[to-issues](./skills/productivity/to-issues/SKILL.md)** — An improvement on Matt Pocock's `to-issues`: break a plan into tracer-bullet vertical slices, publish them, and wire the blocked-by/parent edges into native GitHub sub-issues + dependencies so the tracker shows the real tree (not just prose). Use when turning a plan into issues.

### Misc

Tools kept around but rarely used. None yet.

## Local Development

```bash
./scripts/list-skills.sh
./scripts/link-skills.sh
./scripts/link-skills-all.sh
python3 scripts/generate-skill-artifacts.py
python3 scripts/generate-skill-artifacts.py --check
python3 scripts/evaluate-skill-router.py
```

The generator derives every Codex picker name from the skill's kebab-case `name`. It emits `agents/openai.yaml`, the catalog, router reference, docs, and plugin list; generated files are not hand-edited.

See [Codex metadata](./docs/openai-yaml.md) for the supported prompts, icons, colors, tool dependencies, and product policies.
