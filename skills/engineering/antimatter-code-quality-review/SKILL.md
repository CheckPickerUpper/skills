---
name: antimatter-code-quality-review
description: "Total annihilation: no finding survives unless it survives refutation. An unusually strict maintainability and structural-quality audit of a diff — review frame, intent/spec fit, repo standards, abstraction quality, cohesion, type/boundary cleanliness, duplication, control-flow tangles, missed extractions and invented variation, data structures whose cost grows faster than they need to, allocation on repeating paths, and correct-by-construction opportunities. Use for a deep code-quality audit, a harsh pre-merge review, or to determine what structural change makes a class of bug impossible rather than merely caught. Stricter than a conventional review because every finding must survive an adversarial refutation pass, ship with a concrete before→after, and prove it preserves behavior. Severity theater is prohibited: only provable findings are reported."
---

# /antimatter-code-quality-review

Total annihilation: no finding survives unless it survives refutation.

## Lineage

Antimatter draws from Cursor's [Thermo-Nuclear Code Quality Review](https://github.com/cursor/plugins/blob/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md), Matt Pocock's [skills](https://github.com/mattpocock/skills), especially his [code-review skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md), and Ozzy's correctness-first design philosophy. The result is an elevated correctness-oriented code-quality review: ambitious about structure, but unwilling to report anything it cannot prove.

## Overview

This skill performs the strictest available structural read of a change. It targets the ambitious restructurings a conventional review omits — simplifications that preserve behavior while collapsing whole categories of complexity — and reports them with zero tolerance for false positives.

The standard is not aggression. The dominant failure mode of a strict review is **severity theater**: findings invented or inflated to satisfy a "be harsh" instruction, which buries real signal and degrades trust. The standard here is annihilation. A finding is reported only if it survives an adversarial refutation pass, carries a concrete before→after, and is shown to preserve behavior. Everything that fails any of those is destroyed before output.

The report is short, ranked, and entirely load-bearing. A review incapable of returning a clean approval is itself defective.

## Scope

The review surface is the diff against a fixed point. If the user supplied a commit, branch, tag, PR, or range, use that. Otherwise infer the canonical base from the checked-out branch or remote default branch, state the fixed point, and continue. Code outside the diff is examined only where a finding's blast radius reaches it, and that reach is stated explicitly. Reviewing untouched code is the cause of runaway, off-target reviews.

## Excluded

Whitespace, naming-only changes, and any defect a linter or formatter catches are out of scope. Those surfaces are owned by automated tooling and are not reported here.

## Procedure

The phases run in order. No finding is reported from Phase 1; findings are provisional until Phase 2 destroys the unprovable ones.

### Phase 0 — Review frame
Pin the comparison before reviewing:

- Resolve the fixed point and use a merge-base diff when comparing branches, usually `git diff <fixed-point>...HEAD`.
- Capture the commit list, usually `git log <fixed-point>..HEAD --oneline`.
- Fail early on an unresolved fixed point or an empty diff.
- State the exact diff command and any range assumptions in the report.

Identify the work's intent before judging fit:

- Prefer issue or PR references from commit messages and branch names.
- Use a spec, PRD, or task file the user passed explicitly.
- Search likely local homes such as `docs/`, `specs/`, `.scratch/`, and repo knowledge folders for files matching the branch or feature.
- If no intent source exists, skip spec-fit findings and state that only structural and standards review was possible.

Inventory local standards before applying generic taste:

- Read repo guidance such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, package docs, and relevant module docs.
- Inventory existing conventions, shared utilities, abstractions, and type vocabulary before proposing new structure.
- Let documented repo standards override generic smell prompts. A proposal that re-implements an existing helper is itself a finding, not an improvement.

### Phase 1 — Per-dimension review (provisional)
Each dimension below is examined independently. A silently skipped dimension is a defect; a dimension with no finding is reported as clean with its reason, never omitted.

### Phase 2 — Refutation gate (annihilation)
Each provisional finding is subjected to an adversarial pass whose objective is to refute it, defaulting to rejection unless the evidence compels otherwise. A finding is destroyed when it:

- lacks a concrete before→after that can be written,
- cannot be shown to preserve behavior,
- rests on taste with no named defect, or
- is subsumed by a stricter finding.

Survivors are real. The remainder is destroyed without comment.

### Phase 3 — Rank and report
Survivors are ranked by blast radius and partitioned into *Blocks merge* and *Suggestion*. The report closes with the dimension coverage map and an explicit verdict: approve, approve with suggestions, or block.

## Dimensions

- **Cohesion** — whether a unit has more than one reason to change. Measured in responsibilities, not lines.
- **Abstraction quality** — whether a simpler reframing eliminates a category of complexity, or whether a thin wrapper or identity abstraction adds indirection without clarity.
- **Control flow** — whether branching has grown where a model belongs. Repeated conditionals over the same shape indicate a missing type.
- **Types and boundaries** — unnecessary optionality, `any` / `unknown`, cast-heavy code, and loosely-shaped objects standing in for explicit typed models.
- **Duplication and ownership** — feature-specific logic leaking into shared utilities, re-implemented canonical helpers, and architectural-boundary drift.
- **Intent fit** — whether the diff omits required behavior, adds behavior the intent source did not ask for, or implements the right words with the wrong observable behavior. Skip this dimension when no intent source was found.
- **Algorithmic cost** — whether the data structure fits the operation performed on it. A lookup by scanning, a loop nested over the same collection, a sort where one pass answers the question: each names a shape the data could have had instead.
- **Allocation** — whether the change allocates on a path that repeats. A collection, closure, or copy built fresh per call is free once and expensive every frame.
- **Generalization** — whether one form is written twice under two names, and whether an abstraction's parameters are ones some instance actually supplies. Both directions are findings: a hand-written second copy of a nameable form, and a knob no instance turns.
- **Correct-by-construction** — whether a type, boundary, or data-shape change renders the finding's entire class unrepresentable rather than caught. This is the highest-value finding when available.

## Smell prompts

Use these as search prompts only. They are never findings by themselves, and each must still survive the refutation gate:

- **Cohesion:** divergent change, shotgun surgery.
- **Abstraction quality:** speculative generality, middle man.
- **Control flow:** repeated switches or equivalent repeated `if` cascades.
- **Types and boundaries:** data clumps, primitive obsession, refused inheritance contracts.
- **Duplication and ownership:** duplicated code, feature envy, message chains.
- **Intent fit:** missing requirement, scope creep, or a behavior that satisfies the letter of the request while violating its observable purpose.
- **Algorithmic cost:** iteration nested over one collection, lookup by scan, repeated sorting, a value recomputed inside a loop that cannot change it.
- **Allocation:** a collection, closure, or copy built per call; rebuilding a whole collection to append one element; a defensive copy of a value nobody mutates.
- **Generalization:** the same shape written twice under two names; a type parameter, strategy seam, or config field no instance varies.

## Route a survivor to its lens

A survivor usually has a shape with a known procedure behind it. Load the matching reference and fold its result into the finding's before → after. These references are self-contained; nothing outside this skill has to be installed.

| Load | When the survivor is |
|---|---|
| `references/construction-lens.md` | a state the code can be told to be in and should not be able to be: a redundant field, a union arm that means nothing, a check standing where a shape belongs |
| `references/generalization-lens.md` | one form written twice under two names, or a parameter no instance supplies |
| `references/performance-lens.md` | an operation whose cost grows faster than it needs to, or work allocated on a path that repeats |

Route only survivors. A provisional finding that has not passed Phase 2 does not earn a lens.

## Required evidence per finding

Each surviving finding carries:

1. **Before → after.** A concrete restructuring. A finding whose "after" cannot be written is hand-waving and is destroyed.
2. **Defect removed.** The specific complexity or bug the change eliminates — what fails today that would not.
3. **Behavior-preservation.** The basis for equivalence: pure move, test coverage, or type check. A change whose equivalence cannot be guaranteed is downgraded to a flagged risk.
4. **Blast radius.** The call sites and modules affected. This determines rank. A performance finding ranks by what grows and how often its path runs, not by how many call sites it has: one line on a per-frame path outranks a wide but cold change.
5. **Cost.** Churn and regression risk. A high-cost, low-payoff restructuring is a note, not a blocker.

## File size

Crossing approximately 1,000 lines triggers examination, never a verdict. The governing invariant is cohesion: a generated table or flat data file of any size is acceptable; a 300-line file with six reasons to change is not. The reported finding is the missing decomposition, not the line count. The threshold initiates the investigation; it does not conclude it.

## Approval

A clean approval is a valid and expected outcome. When a change introduces no structural regression, omits no plausible simplification, and leaks across no boundary, it is approved without qualification. A manufactured finding offered as evidence of thoroughness is the severity theater this skill exists to eliminate.

## Worked example

A change adds a third `if (feature === 'x')` branch inside a shared `renderRow` used by four call sites.

- **Provisional finding (Phase 1):** feature-specific branching in a shared helper.
- **Refutation (Phase 2):** the helper is confirmed shared — four callers, one branch-dependent. The finding survives.
- **Before → after:** the feature-specific rendering is lifted into the single caller that requires it; `renderRow` accepts a rendered cell rather than a feature flag.
- **Defect removed:** the shared helper otherwise accumulates one branch per feature indefinitely, and every unrelated caller carries logic it never uses.
- **Behavior-preservation:** a pure move of the branch body into the caller; types check; the other three callers are untouched.
- **Blast radius:** four call sites, one modified.
- **Correct-by-construction upgrade:** `renderRow` accepts `Cell` rather than `feature: string`, rendering "feature flag in shared render" unrepresentable rather than removed once.
- **Severity:** Blocks merge — the established shape compounds.

## Contract

1. Pin and state the fixed point, diff command, and commit range before reviewing.
2. Identify intent and standards sources; state when either is absent.
3. Review the diff surface; widen only where blast radius requires, and state where it does.
4. Inventory existing abstractions before proposing new ones.
5. Examine every applicable dimension; report clean dimensions as clean and unavailable dimensions as unavailable.
6. Destroy every finding that fails refutation, lacks a before→after, or cannot be shown behavior-preserving.
7. Route each survivor whose shape matches a lens through that reference before writing its before → after.
8. Rank survivors by blast radius; partition blocks-merge from suggestion; attach cost to each.
9. Approve cleanly when the change is clean. Report every clean dimension by name, including the ones that found nothing.
