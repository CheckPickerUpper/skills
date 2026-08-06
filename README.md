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
- **[pizza1](./skills/engineering/pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, transition size, compatibility, legacy paths, or scope.
- **[readonly](./skills/engineering/readonly/SKILL.md)** — Prove, don't guess. A user-invoked modifier for codebase questions and other skills: exhaust read-only evidence, avoid "likely" answers when facts can be checked, and stop before implementation, issues, commits, or remote changes.
- **[stacked-prs](./skills/engineering/stacked-prs/SKILL.md)** — Relabel is not restack. Build, restack, and land a chain of dependent PRs so each layer reviews as one focused change; catches the stack that looks correct in the UI because its base was only relabelled and the branch was never rebased onto the layer below.

### Productivity

General workflow tools.

- **[grill-with-docs-requiem](./skills/productivity/grill-with-docs-requiem/SKILL.md)** — A design interview that asks useful batches, infers obvious answers, and records settled domain language and ADRs as the conversation progresses. Use when sharpening a plan while maintaining docs.
- **[to-issues](./skills/productivity/to-issues/SKILL.md)** — An improvement on Matt Pocock's `to-issues`: break a plan into tracer-bullet vertical slices, publish them, and wire the blocked-by/parent edges into native GitHub sub-issues + dependencies so the tracker shows the real tree (not just prose). Use when turning a plan into issues.

### Misc

Tools kept around but rarely used. None yet.

## Local Development

```bash
./scripts/list-skills.sh
./scripts/link-skills.sh
```
