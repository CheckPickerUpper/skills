# Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

- **[antimatter-code-quality-review](./antimatter-code-quality-review/SKILL.md)** — Deep code-quality and pre-merge review of a commit, PR, branch, or diff. Audit correctness, intent, naming, cohesion, types, boundaries, control flow, duplication, cost, allocation, and generalization. Check predictability: does a feature or fix create a second way to perform a capability the codebase already has? Compare existing implementations, reuse or extend sound patterns, and extract shared behavior without letting one feature own the abstraction or inventing flexibility. Every finding needs evidence, a concrete before-and-after, behavior preservation, and adversarial refutation.
- **[antimatter-codebase-structure-review](./antimatter-codebase-structure-review/SKILL.md)** — Audits hierarchy, naming, ownership, dependency boundaries, and growth readiness; every finding must survive refutation and specify an evidence-backed change.
- **[pizza1](./pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, transition size, compatibility, legacy paths, or scope.
- **[readonly](./readonly/SKILL.md)** — Prove, don't guess. A user-invoked modifier for codebase questions and other skills: exhaust read-only evidence, avoid "likely" answers when facts can be checked, and stop before implementation, issues, commits, or remote changes.
