# Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

- **[antimatter-code-quality-review](./antimatter-code-quality-review/SKILL.md)** — Total annihilation: no finding survives unless it survives refutation. Inspired by Cursor's [Thermo-Nuclear review](https://github.com/cursor/plugins/blob/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md), [Matt Pocock's skills](https://github.com/mattpocock/skills), and correctness-first design philosophy; pins the diff frame, checks intent and repo standards, and only reports provable findings.
- **[pizza1](./pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, transition size, compatibility, legacy paths, or scope.
- **[readonly](./readonly/SKILL.md)** — Prove, don't guess. A user-invoked modifier for codebase questions and other skills: exhaust read-only evidence, avoid "likely" answers when facts can be checked, and stop before implementation, issues, commits, or remote changes.
- **[stacked-prs](./stacked-prs/SKILL.md)** — Relabel is not restack. Build, restack, and land a chain of dependent PRs so each layer reviews as one focused change; catches the stack that looks correct in the UI because its base was only relabelled and the branch was never rebased onto the layer below.
