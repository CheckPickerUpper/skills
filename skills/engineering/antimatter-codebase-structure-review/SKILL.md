---
name: antimatter-codebase-structure-review
description: "Pedantic structural audit of a commit, PR or branch, selected directory or module, or an entire codebase — hierarchy, nesting, naming, ownership, dependency boundaries, and growth readiness. Use when a change may distort repository shape, when a file or folder needs structural review, or when deciding whether to reorganize before expansion. Every finding must survive adversarial refutation and include evidence plus a concrete current→proposed change."
---

# /antimatter-codebase-structure-review

Pedantic structural audit of a scoped codebase surface.

The review asks whether the structure is clear, cohesive, appropriately
nested, consistently named, honestly bounded, and ready for evidence-backed
growth. Names and hierarchy are first-class design decisions.

Pedantic means exhaustive and explicit. It does not mean inventing findings
from personal taste. A structural metric is a search prompt, never a verdict.

## Relationship to antimatter

`antimatter-code-quality-review` primarily reviews code changes for
maintainability, correctness, abstraction quality, control flow, types,
boundaries, duplication, cost, allocation, and generalization.

This skill reviews the shape surrounding that code:

- where files and folders belong;
- whether nesting communicates real ownership;
- whether names remain clear outside their parent-folder context;
- whether the structure is too flat, too deep, or prematurely elaborate; and
- whether likely expansion will produce a coherent tree or a dumping ground.

Use this skill alongside antimatter when a commit or PR has structural
consequences. Keep the skills separate because their review surfaces differ.
This skill shares antimatter's adversarial refutation standard.

## Scope modes

Choose the mode that matches the user's request:

- **Commit** — review one commit's changed paths against its parent, unless
  the user supplies another fixed point.
- **PR or branch** — review the merge-base diff against the target branch, or
  the exact range supplied by the user.
- **Selected area** — review a supplied directory, module, feature, or
  conceptual code area in its current repository context.
- **Entire codebase** — review the repository's overall structure.

For commit and PR reviews, inspect the changed surface first. Widen only to
parent directories, relevant siblings, direct consumers, and established
conventions needed to prove a finding. State every meaningful widening.

For selected-area and whole-codebase reviews, a historical fixed point is
optional. Review the current structure and state when no historical
comparison was used.

## Procedure

The phases run in order. Findings are provisional until the refutation phase.
Every phase ends with a completion criterion; do not advance on a vague sense
of understanding.

### Phase 0 — Frame the review

Resolve:

- the scope mode;
- the exact commit, branch, PR range, path, module, feature, or repository;
- the fixed point when reviewing a commit or PR;
- the work's intent, when available;
- repository guidance and naming conventions; and
- generated, vendored, temporary, and build-output exclusions.

For a commit, compare the commit with its parent unless the user supplied a
different comparison. For a branch or PR, use the merge base with the target
branch. If the user supplied a commit, branch, tag, PR, or range, preserve it
instead of inventing a narrower target.

Read local guidance such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
package documentation, and relevant module documentation before applying
generic structural preferences.

State the exact comparison, path scope, intent source, standards sources, and
exclusions in the final report. If a fixed point cannot be resolved for a
change review, stop with that blocker. A general-area review can proceed
without one.

**Complete when:** the target, comparison basis, intent source, standards,
exclusions, and any intentionally widened context are explicit.

### Phase 1 — Map the current shape

Build an evidence-based map of the relevant structure:

- folder and file hierarchy;
- nesting depth and breadth;
- feature, domain, and technical groupings;
- source, test, fixture, generated, and configuration placement;
- module boundaries and import direction;
- existing names for similar concepts; and
- catch-all locations such as `utils`, `common`, `shared`, `misc`, or generic
  `components` folders.

Classify relevant paths by ownership and role before judging their placement.
Inspect the smallest surrounding context that can explain the target. Do not
turn a scoped review into an unrelated repository tour.

When a tree communicates the issue materially better than prose, include a
compact current tree. A projected tree is allowed only for an evidence-backed
growth scenario; it is not a license to invent architecture.

**Complete when:** every relevant file and folder has an understood owner,
role, grouping, and relationship to nearby structure.

### Phase 2 — Audit nesting and grouping

Examine every meaningful level of the scoped hierarchy.

A directory earns its level when it communicates a real boundary such as:

- domain ownership;
- feature ownership;
- lifecycle or deployment boundary;
- technical boundary; or
- a stable grouping that prevents ambiguity or future collision.

For each questionable level, test:

- whether removing the level would mix unrelated owners;
- whether adding the level would merely wrap one file or repeat its parent;
- whether sibling paths represent the same kind of thing;
- whether one feature is split across unrelated branches;
- whether a technical-layer tree scatters code that changes together;
- whether the path makes ownership obvious;
- whether the grouping follows the repository's existing convention; and
- whether the level solves a current problem or only an imagined future one.

Classify the shape as **earned**, **redundant**, **missing**, **inconsistent**,
or **premature** only when evidence supports the classification.

Depth, breadth, file count, and one-file directories are inspection prompts,
not automatic defects. A deep tree can be correct; a flat tree can be
incoherent.

**Complete when:** every questionable hierarchy level is classified with a
reason grounded in ownership, ambiguity, dependency shape, convention, or
evidence-backed growth.

### Phase 3 — Audit names

Evaluate names both in context and in isolation.

Run these tests:

1. **Isolated-name test:** read the basename without relying on its parent
   folder. State what the file or folder represents or owns.
2. **Role test:** determine whether the name communicates its role, such as
   parser, schema, client, repository, test, fixture, or view.
3. **Domain test:** determine whether the name identifies the relevant domain
   or feature when that distinction matters.
4. **Convention test:** compare it with names for equivalent artifacts in the
   repository.
5. **Ownership test:** determine whether the name points toward the actual
   owner rather than a generic shared location.
6. **Collision test:** check for duplicate, near-synonymous, or collision-prone
   names.

Review for:

- generic names whose purpose cannot be inferred;
- names that rely entirely on parent-folder context;
- inconsistent nouns, verbs, plurality, tense, or suffixes;
- suffixes such as `Service`, `Manager`, `Handler`, `Client`, `Repository`,
  or `Controller` used with inconsistent meaning;
- names that conceal ownership or lifecycle;
- names that force the reader to open the file to discover its role; and
- names that over-specify implementation while hiding purpose.

Recognize stable framework, language, test, generated, and repository
conventions such as `index`, `mod`, `__init__`, and test suffixes. A shorter
name can be correct when the convention is stable and ambiguity is absent.

A name is not a finding merely because a longer or more fashionable name
exists. Report it only when ambiguity, collision, ownership confusion,
inconsistent meaning, or demonstrated maintenance cost is present.

**Complete when:** every relevant name is classified as clear, conventionally
acceptable, ambiguous, misleading, or inconsistent, with a concrete reason.

### Phase 4 — Audit ownership, cohesion, and boundaries

Review whether the hierarchy reflects how the code changes and depends.

Examine:

- multiple unrelated reasons for a file or folder to change;
- one feature owning logic placed in another feature's folder;
- shared folders accumulating feature-specific behavior;
- duplicate concepts with no clear canonical owner;
- cross-boundary imports and cyclic dependencies;
- barrel files that hide ownership or create accidental coupling;
- type, utility, or component folders becoming unbounded collections;
- tests, fixtures, and mocks placed far from the code they describe; and
- a folder name promising a boundary that its imports violate.

Prefer structures where ownership is visible from the path and dependency
direction is legible from the tree. Existing shared locations are evidence of
convention, not proof that every new consumer belongs there.

**Complete when:** each reported ownership or boundary concern identifies the
responsible owner, violated boundary, affected consumers, and relevant
dependency evidence.

### Phase 5 — Test growth readiness

Predict growth only from evidence. Use existing sibling files, repeated recent
additions, the commit or PR intent, domain vocabulary, TODOs, issue references,
and local documentation.

When useful, construct no more than three plausible next additions. For each,
simulate:

- its natural location;
- its isolated and contextual name;
- whether another nesting level would be needed;
- whether an existing folder would become a dumping ground;
- whether ownership would remain clear; and
- whether dependency direction would remain truthful.

Recommend preparing now when the current structure already creates a defect,
or when the next evidence-backed addition would repeat a demonstrated
structural failure and the remedy is low-risk.

Recommend waiting when the restructuring exists mainly for hypothetical scale,
when no likely addition is supported by evidence, or when the current shape
remains clear.

**Complete when:** every growth recommendation is tied to an observable
pattern or explicit intent, and each scenario has a prepare-now, prepare-later,
or leave-as-is conclusion.

### Phase 6 — Refute provisional findings

Attempt to destroy every finding before reporting it. Default to rejection
unless the evidence compels survival.

Destroy a finding when:

- it is only a preference;
- a documented repository convention explains the structure;
- the alleged ambiguity disappears under normal project conventions;
- the proposed change has no concrete defect to remove;
- the concern is owned by a formatter, linter, generator, or framework;
- the restructuring is speculative;
- the scope or blast radius cannot be established;
- preservation of imports, ownership, or observable behavior cannot be shown;
  or
- a stronger finding subsumes it.

Every survivor needs a writable current → proposed change. A finding whose
“after” cannot be described precisely is hand-waving and is destroyed.

**Complete when:** every provisional finding is destroyed or carries the full
evidence required by the finding contract below.

### Phase 7 — Report the result

Report in this order:

1. Review mode and exact scope.
2. Fixed point and comparison, when applicable.
3. Intent and repository standards sources.
4. Current structural map or scoped tree.
5. Coverage for every applicable dimension.
6. Surviving findings ranked by blast radius and urgency.
7. Growth scenarios and prepare-now decisions.
8. Explicit verdict.

For commit and PR reviews, partition findings into **Blocks merge** and
**Suggestion**. For selected-area and whole-codebase reviews, partition them
into **Fix now**, **Prepare later**, and **Leave as-is**.

**Complete when:** the report states what was reviewed, what was clean, what
survived refutation, what should change, and why.

## Coverage dimensions

Examine each applicable dimension independently. Report a dimension as clean
with its reason; report it as unavailable with the reason it could not apply.

- **Hierarchy and nesting** — whether grouping and depth express real
  boundaries.
- **Naming clarity** — whether files and folders communicate purpose,
  ownership, and role without unnecessary context.
- **Ownership and cohesion** — whether code that changes together is grouped
  together and each unit has a clear owner.
- **Dependency shape** — whether imports, cycles, barrels, and boundaries
  reflect the hierarchy.
- **Growth readiness** — whether likely additions have natural homes without
  speculative structure.
- **Intent fit** — for commits and PRs, whether the structural result serves
  the stated intent without unrequested organizational scope.
- **Correct-by-construction structure** — whether a path or boundary change
  makes a class of ownership or placement error difficult or impossible to
  represent.

## Required evidence per finding

Each surviving finding carries:

1. **Location** — exact file, folder, path, or boundary.
2. **Observation** — what the current structure does.
3. **Defect removed** — the concrete ambiguity, coupling, growth failure, or
   maintenance cost.
4. **Current → proposed** — exact path, tree, grouping, or name change.
5. **Evidence** — siblings, imports, consumers, history, intent, conventions,
   or an observed expansion pattern.
6. **Growth impact** — what future addition becomes easier or harder.
7. **Preservation basis** — pure move, import update, type check, tests, build
   proof, or explicitly stated migration risk.
8. **Blast radius** — affected files, modules, consumers, and owners.
9. **Cost** — churn, migration effort, and regression risk.
10. **Timing** — why it should change now, later, or never.

Rank by blast radius and urgency, not by how visually surprising the tree or
name appears.

## Decision rules

- Treat depth, breadth, file count, and naming length as prompts for
  inspection, never as verdicts.
- Prefer the minimum structure that makes ownership, placement, and growth
  clear.
- Let explicit repository conventions inform the review, while checking that
  the convention still communicates the intended boundary.
- Treat a generic folder as a finding only when its contents demonstrate
  unclear ownership, repeated placement decisions, or boundary leakage.
- Treat a new hierarchy level as a finding only when it is redundant,
  misleading, inconsistent, or already required by visible growth.
- Treat a name as a finding only when it causes a concrete ambiguity, collision,
  ownership problem, or maintenance cost.
- Use growth scenarios to test the current shape, not to justify architecture
  for unsupported futures.
- Review untouched paths only when they explain the target's structure or
  blast radius, and state that widening.
- Preserve a clean approval as the correct result when no finding survives
  refutation.

## Output contract

Use this shape:

## Structural review

Mode: commit, PR/branch, selected area, or entire codebase
Scope: ...
Baseline: ... or no historical comparison
Intent: ... or unavailable
Standards: ...
Work state: analysis only

### Current shape

...

### Coverage

| Dimension | Status | Evidence or reason |
|---|---|---|
| Hierarchy and nesting | clean / findings / unavailable | ... |
| Naming clarity | clean / findings / unavailable | ... |
| Ownership and cohesion | clean / findings / unavailable | ... |
| Dependency shape | clean / findings / unavailable | ... |
| Growth readiness | clean / findings / unavailable | ... |
| Intent fit | clean / findings / unavailable | ... |
| Correct-by-construction structure | clean / findings / unavailable | ... |

### Findings

For each survivor, include:

- Rank and verdict.
- Location.
- Observation.
- Defect removed.
- Current → proposed.
- Evidence and growth impact.
- Preservation basis.
- Blast radius.
- Cost and timing.

### Growth projection

Show only evidence-backed scenarios. Include the current placement and the
projected placement when the tree materially clarifies the decision.

### Verdict

Approve, approve with suggestions, block, fix now, prepare later, or leave
as-is. Explain the decision in one concise paragraph.

Completion criterion: a reader can verify the scope, current shape, complete
dimension coverage, every surviving finding, and the verdict without
reconstructing the agent's reasoning.

## Approval standard

A clean approval is valid and expected. Approve when the scoped structure is
coherent, names are sufficiently clear, boundaries are truthful, growth
scenarios do not compel preparation, and no evidence-backed restructuring
survives refutation.

A manufactured finding offered as evidence of thoroughness is a failure of
this skill.
