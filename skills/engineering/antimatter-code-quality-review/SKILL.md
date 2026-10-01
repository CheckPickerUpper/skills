---
name: antimatter-code-quality-review
description: "Deep code-quality and pre-merge review of a commit, PR, branch, or diff. Audit correctness, intent, naming, cohesion, types, boundaries, control flow, duplication, cost, allocation, and generalization. Check predictability: does a feature or fix create a second way to perform a capability the codebase already has? Compare existing implementations, reuse or extend sound patterns, and extract shared behavior without letting one feature own the abstraction or inventing flexibility. Every finding needs evidence, a concrete before-and-after, behavior preservation, and adversarial refutation."
short_description: "Evidence-backed code review, including predictable patterns and reusable abstractions."
allow_implicit_invocation: true
---

# /antimatter-code-quality-review

<supporting-info>
Total annihilation: no finding survives unless it survives refutation.

## Lineage

Antimatter draws from Cursor's [Thermo-Nuclear Code Quality Review](https://github.com/cursor/plugins/blob/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md), Matt Pocock's [skills](https://github.com/mattpocock/skills), especially his [code-review skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md), and Ozzy's correctness-first design philosophy. The result is an elevated correctness-oriented code-quality review: ambitious about structure, but unwilling to report anything it cannot prove.

## Overview

This skill performs the strictest available structural read of a change. It targets the ambitious restructurings a conventional review omits — simplifications that preserve behavior while collapsing whole categories of complexity — and reports them with zero tolerance for false positives.

The standard is not aggression. The dominant failure mode of a strict review is **severity theater**: findings invented or inflated to satisfy a "be harsh" instruction, which buries real signal and degrades trust. The standard here is annihilation. A finding is reported only if it survives an adversarial refutation pass, carries a concrete before→after, and is shown to preserve behavior. Everything that fails any of those is destroyed before output.

The report is short, ranked, and entirely load-bearing. A review incapable of returning a clean approval is itself defective.
</supporting-info>

<what-to-do>
## Scope

The review surface is the diff against a fixed point. If the user supplied a commit, branch, tag, PR, or range, use that. Otherwise infer the canonical base from the checked-out branch or remote default branch, state the fixed point, and continue. Search outside the diff for implementations of capabilities the change introduces or materially changes, and inspect relevant definitions and callers. Widen further only to establish a finding's blast radius. State the comparison paths and each widening; keep unrelated untouched code outside the review.

Use the repository's available search, file-reading, and version-control tools. All procedures and references required by this skill are included here; no other skill, plugin, client-specific tool, or subagent is required. Review and propose changes; implementation requires separate authorization.

## Excluded

Whitespace, style-only naming changes, and any defect a linter or formatter catches are out of scope. Style includes length, casing, and similar preferences. A name that contradicts its definition is not a style-only naming change and is in scope under Naming truth.

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

- Read the instruction files that apply to the running agent, plus repository guidance such as `CONTRIBUTING.md`, `CODING_STANDARDS.md`, package docs, and relevant module docs. Instructions for another client do not define this client's behavior.
- Inventory existing conventions, shared utilities, abstractions, and type vocabulary before proposing new structure.
- Let documented repo standards override generic smell prompts, while checking the behavior they require. An existing pattern earns reuse through correctness and fit; prevalence alone does not justify it.

### Phase 1 — Definition-first, then per-dimension review (provisional)
Read the definition before you write the finding. For every file, type, function, or field a finding will name, open that file and read the definition at the line you will cite: the struct's fields, the enum's variants, the function's body and callers. Do this before writing a single word of the finding. Cite the line you read. Never infer what a thing is from its name, its file name, a docstring, a comment, a PR body, or an issue body; those are claims about the code, and the definition is the code. When the name and the definition disagree, the disagreement is itself a finding (see Naming truth).

Each dimension below is examined independently. A silently skipped dimension is a defect; a dimension with no finding is reported as clean with its reason, never omitted.

### Predictability comparison — required during Phase 1

For every capability introduced or materially changed, complete this comparison before refutation. Group changed sites only when they perform the same capability.

1. **Describe the behavior.** Read the changed definitions and callers. State what they do, the guarantee they must preserve, and the changed paths.
2. **Find existing ways to do it.** Search repository code and relevant documentation by behavior, domain concepts, operations, and callers. Follow candidate definitions and call sites even when their names or code differ. A search for the new function's name alone is insufficient. Record the search scope and terms; distinguish a pre-existing implementation from one added by this diff.
3. **Compare requirements.** Read each relevant candidate's implementation. Compare inputs, results, failures, side effects, state transitions, lifecycle, and ownership where applicable. State the shared guarantee and the differences that affect correctness. Similar spelling is not proof of shared behavior; different spelling is not proof of different behavior.
4. **Choose the resulting shape.** Use a correct existing capability when it fits. Extend it when the new requirement is a real variation of the same behavior. Generalize when a shared operation is trapped in a feature-specific implementation or name; read `references/generalization-lens.md` before judging that proposal. Keep implementations separate when a concrete requirement or boundary makes unification incorrect, and name that difference. If the existing pattern is wrong, describe the corrected shared shape and its affected consumers rather than recommending another copy of the defect.
5. **Record the result.** Include the comparison table below, including clean results. When no relevant implementation is found, report where and how you searched. Still examine whether the changed code expresses a reusable operation confined to its first instance; consumer count does not settle that question. Mark incomplete searches as unavailable with the concrete missing access or evidence.

| Capability and changed paths | Existing implementation or search scope | Shared guarantee and necessary differences | Decision and evidence |
|---|---|---|---|
| ... | ... | ... | reuse / extend / generalize / separate / correct the pattern; definition and caller locations, or search evidence and resulting decision when no existing match is found |

**Complete when:** every introduced or materially changed capability has a comparison row supported by inspected definitions or a recorded search. For a change with no behavioral capability to compare, report predictability as not applicable and state why. A completed search is coverage, not an automatic finding. Findings still need a concrete defect, a behavior-preserving proposal, and Phase 2 refutation.

### Phase 2 — Refutation gate (annihilation)
Each provisional finding is subjected to an adversarial pass whose objective is to refute it, defaulting to rejection unless the evidence compels otherwise. A finding is destroyed when it:

- lacks a concrete before→after that can be written,
- cannot be shown to preserve behavior,
- rests on taste with no named defect, or
- is subsumed by a stricter finding.

Survivors are real. The remainder is destroyed without comment.

### Phase 3 — Rank and report
Survivors are ranked by blast radius and partitioned into *Blocks merge* and *Suggestion*. Include the predictability comparison, then close with the dimension coverage map and an explicit verdict: approve, approve with suggestions, or block.

## Dimensions

- **Naming truth** — whether a name predicts the definition. A name lies when a reader from the domain would predict fields, storage, or behavior the definition does not have: `LocalFsBlobStore` holding a `HashMap`, an `Outcome` that is an `Error`, a `check` that returns `Ready` without checking. Style, length, and casing stay excluded; only a name that contradicts its definition is a finding. Evidence: the name, the definition at file:line, and the wrong prediction a reader would make. After: the term the domain already uses. Correct-by-construction upgrade: the type's shape and its name stop being two owners of one fact.
- **Cohesion** — whether a unit has more than one reason to change. Measured in responsibilities, not lines.
- **Abstraction quality** — whether a simpler reframing eliminates a category of complexity, or whether a thin wrapper or identity abstraction adds indirection without clarity.
- **Control flow** — whether branching has grown where a model belongs. Repeated conditionals over the same shape indicate a missing type.
- **Types and boundaries** — unnecessary optionality, `any` / `unknown`, cast-heavy code, and loosely-shaped objects standing in for explicit typed models.
- **Duplication and ownership** — feature-specific logic leaking into shared utilities, re-implemented canonical helpers, and architectural-boundary drift.
- **Predictability** — whether equivalent requirements follow a coherent implementation pattern, and whether necessary differences are explicit. Compare behavior across the codebase, including different-looking implementations. Report unexplained divergence only with the concrete competing paths, maintenance or correctness defect, and proposed shared shape.
- **Intent fit** — whether the diff omits required behavior, adds behavior the intent source did not ask for, or implements the right words with the wrong observable behavior. Skip this dimension when no intent source was found.
- **Algorithmic cost** — whether the data structure fits the operation performed on it. A lookup by scanning, a loop nested over the same collection, a sort where one pass answers the question: each names a shape the data could have had instead.
- **Allocation** — whether the change allocates on a path that repeats. A collection, closure, or copy built fresh per call is free once and expensive every frame.
- **Generalization** — whether a reusable operation is confined to its first instance, written again under another name, or burdened with invented variation. Use `references/generalization-lens.md` whenever reviewing extraction, reuse, extension, or an abstraction's name or parameters.
- **Correct-by-construction** — whether a type, boundary, or data-shape change renders the finding's entire class unrepresentable rather than caught. This is the highest-value finding when available.

## Smell prompts

Use these as search prompts only. They are never findings by themselves, and each must still survive the refutation gate:

- **Cohesion:** divergent change, shotgun surgery.
- **Abstraction quality:** speculative generality, middle man.
- **Control flow:** repeated switches or equivalent repeated `if` cascades.
- **Types and boundaries:** data clumps, primitive obsession, refused inheritance contracts.
- **Duplication and ownership:** duplicated code, feature envy, message chains.
- **Predictability:** a feature-local replacement for a sound existing capability; equivalent state transitions or failure handling implemented differently; an existing pattern copied despite a known defect.
- **Intent fit:** missing requirement, scope creep, or a behavior that satisfies the letter of the request while violating its observable purpose.
- **Algorithmic cost:** iteration nested over one collection, lookup by scan, repeated sorting, a value recomputed inside a loop that cannot change it.
- **Allocation:** a collection, closure, or copy built per call; rebuilding a whole collection to append one element; a defensive copy of a value nobody mutates.
- **Generalization:** a general operation named after one feature; the same behavior written under different names; a type parameter, strategy seam, or config field whose variation has no basis in the operation's requirements.

## Route a survivor to its lens

A survivor usually has a shape with a known procedure behind it. Load the matching reference and fold its result into the finding's before → after. Reuse the generalization analysis already performed during Phase 1. These references are self-contained; nothing outside this skill has to be installed.

| Load | When the survivor is |
|---|---|
| `references/construction-lens.md` | a state the code can be told to be in and should not be able to be: a redundant field, a union arm that means nothing, a check standing where a shape belongs |
| `references/generalization-lens.md` | an instance-bound operation, competing implementations of shared behavior, or invented variation |
| `references/performance-lens.md` | an operation whose cost grows faster than it needs to, or work allocated on a path that repeats |

Construction and performance lenses apply to survivors. The generalization lens also applies during Phase 1 when the comparison or abstraction review requires it; its analysis remains provisional until Phase 2.

## Required evidence per finding

Each surviving finding carries:

1. **Before → after.** A concrete restructuring. A finding whose "after" cannot be written is hand-waving and is destroyed.
2. **Defect removed.** The specific complexity or bug the change eliminates — what fails today that would not.
3. **Behavior-preservation.** The basis for equivalence: pure move, test coverage, or type check. A change whose equivalence cannot be guaranteed is downgraded to a flagged risk.
4. **Blast radius.** The call sites and modules affected. This determines rank. A performance finding ranks by what grows and how often its path runs, not by how many call sites it has: one line on a per-frame path outranks a wide but cold change.
5. **Cost.** Churn and regression risk. A high-cost, low-payoff restructuring is a note, not a blocker.

For predictability findings, cite both the changed implementation and the existing comparison. Name what the divergence makes a developer get wrong or maintain separately, why the difference is unnecessary, and which callers the proposed reuse, extension, or generalization covers. Account for existing variants and behavior preservation; "match the pattern" alone is not a finding.

## File size

Crossing approximately 1,000 lines triggers examination, never a verdict. The governing invariant is cohesion: a generated table or flat data file of any size is acceptable; a 300-line file with six reasons to change is not. The reported finding is the missing decomposition, not the line count. The threshold initiates the investigation; it does not conclude it.

## Approval

A clean approval is a valid and expected outcome. When a change introduces no structural regression, omits no plausible simplification, and leaks across no boundary, it is approved without qualification. A manufactured finding offered as evidence of thoroughness is the severity theater this skill exists to eliminate.
</what-to-do>

<supporting-info>
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
</supporting-info>

<what-to-do>
## Contract

1. Pin and state the fixed point, diff command, and commit range before reviewing.
2. Identify intent and standards sources; state when either is absent.
3. Review the diff surface; state comparison searches and widenings needed to establish blast radius.
4. Complete the predictability comparison for every introduced or materially changed capability.
5. Examine every applicable dimension; report clean dimensions as clean and unavailable dimensions as unavailable.
6. Destroy every finding that fails refutation, lacks a before→after, or cannot be shown behavior-preserving.
7. Route each survivor whose shape matches a lens through that reference before writing its before → after.
8. Rank survivors by blast radius; partition blocks-merge from suggestion; attach cost to each.
9. Approve cleanly when the change is clean. Report every clean dimension by name, including the ones that found nothing.
</what-to-do>
