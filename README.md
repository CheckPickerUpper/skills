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

- **[antimatter-code-quality-review](./skills/engineering/antimatter-code-quality-review/SKILL.md)** — Total annihilation: no finding survives unless it survives refutation. A strict pre-merge structural audit where every finding ships with a before→after, a behavior-preservation proof, and a correct-by-construction upgrade. Use for a deep code-quality audit with zero severity theater.
- **[pizza1](./skills/engineering/pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, or scope.

### Productivity

General workflow tools.

- **[to-issues](./skills/productivity/to-issues/SKILL.md)** — An improvement on Matt Pocock's `to-issues`: break a plan into tracer-bullet vertical slices, publish them, and wire the blocked-by/parent edges into native GitHub sub-issues + dependencies so the tracker shows the real tree (not just prose). Use when turning a plan into issues.

### Misc

Tools kept around but rarely used. None yet.

## Local Development

```bash
./scripts/list-skills.sh
./scripts/link-skills.sh
```
