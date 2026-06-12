# Skills

[![skills.sh](https://skills.sh/b/CheckPickerUpper/skills)](https://skills.sh/CheckPickerUpper/skills)

Agent skills for correctness-first engineering and clear technical judgment.

These skills are small, composable rules for getting better engineering work from agents. They are tailored toward real engineers, but still usable for vibe coders. They help agents reason from invariants, keep answers inside the user's frame, design simple surfaces, explain tradeoffs clearly, and avoid hiding bad decisions behind convention, churn, scope, or vibes. They are meant to be installed with the open `skills` CLI and adapted per repo.

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

- **[pizza1](./skills/engineering/pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, or scope.

### Productivity

General workflow tools. None yet.

### Misc

Tools kept around but rarely used. None yet.

## Local Development

```bash
./scripts/list-skills.sh
./scripts/link-skills.sh
```
