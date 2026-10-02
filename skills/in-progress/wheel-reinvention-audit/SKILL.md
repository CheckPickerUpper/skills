---
name: wheel-reinvention-audit
description: "Wheel-reinvention audit: inspect implementation plans, code changes, and diffs for standard capabilities hand-rolled where the project, language, platform, framework, or an available dependency could own them. Use during implementation or review when custom parsing, validation, serialization, HTTP, retries, caching, date/time, routing, state, UI primitives, persistence, or data-structure code appears; report a replacement only with manifest and primary-source coverage evidence."
short_description: "Find standard capabilities that custom code should reuse."
allow_implicit_invocation: true
openai:
  interface:
    default_prompt: "Use $wheel-reinvention-audit to find standard capabilities this implementation hand-rolls."
    brand_color: "#B45309"
catalog:
  stage: "review"
  order: 89
  aliases:
    - "audit for wheel reinvention"
    - "check hand-rolled infrastructure"
    - "find the library that already owns this"
  when: "An implementation or diff contains custom infrastructure and the audit must determine whether the project or ecosystem already owns it."
  where_it_fits: "Use during implementation or as a focused review lens before `$code-review`; use `$library-fit` when no code exists and the main task is a build-versus-buy decision."
  success_signals:
    - "Every changed infrastructure behavior is mapped to an existing owner, a verified candidate, or a justified custom owner."
    - "Every replacement finding names the current code, preferred owner, coverage evidence, and required change."
    - "The report separates existing-owner findings from new-dependency options and justified custom work."
---

# Wheel reinvention audit

A wheel-reinvention audit asks whether custom code is carrying a solved capability that a project or ecosystem owner should carry.

<what-to-do>
Run this as an implicit review lens during implementation, design, and review whenever custom infrastructure appears. Audit the proposal or code, produce a decision, and hand an approved change to the implementation workflow. Keep domain rules, orchestration, and boundary adapters custom when they are the project-owned remainder.
</what-to-do>

## Procedure

<what-to-do>

1. State the desired outcome in one plain sentence. Separate it from the proposed implementation, dependency, or first example.

   Completion criterion: `OUTCOME` describes observable behavior without naming how to build it.

2. Pin the audit surface. Use the proposed design when code does not exist, the changed files and their diff when a change exists, or the named files when auditing existing code. Record the paths and comparison point.

   Completion criterion: every conclusion can be traced to a named file, diff, or proposal section.

3. Read the nearest project manifests, lockfiles, relevant configuration, and existing dependency usage. Inventory the language and platform capabilities available to the target code, plus shared helpers already in the repository.

   Completion criterion: the report names every manifest and relevant owner source it checked, including an explicit unavailable result when a manifest is absent.

4. Partition the surface into standard capabilities and project-owned behavior. Standard capabilities include parsing, validation, serialization, HTTP, authentication, retries, caching, date and time, routing, state management, UI primitives, persistence, concurrency, crypto, CLI behavior, and collection algorithms when those categories are present. Project-owned behavior includes domain policy, orchestration, integration glue, and adapters required by an external contract.

   Record every changed custom behavior as a plain labeled entry containing: `Need`, `Current owner`, `Existing project owner`, `Platform or standard-library owner`, `Candidate library`, `Custom remainder`, and `Evidence`.

   Completion criterion: every changed custom block has exactly one entry, including entries whose final owner is custom.

5. Verify owners in this order:

   - an existing project dependency, shared helper, or generated surface;
   - the language standard library, platform API, or framework capability;
   - a known library whose official documentation and repository cover the remaining standard behavior.

   For each candidate, verify the API, semantics, edge cases, compatibility, licence, maintenance, and integration constraints from primary sources when those facts affect the decision. When a current primary source is unavailable, mark the fact unverified and classify the entry `OPEN`. Treat a candidate absent from the manifest as a new-dependency option, not as an existing owner. Treat popularity as no evidence of fit.

   Completion criterion: every non-custom entry names an owner with coverage evidence, or is marked `OPEN` with the smallest check needed to resolve it.

6. Apply the replacement gate to each possible finding. Report a replacement only when all of these are true:

   - the current code performs a named standard capability;
   - the preferred owner covers the same behavior and the target's relevant constraints;
   - adopting it removes caller-owned work, duplicated semantics, or a concrete failure surface;
   - the remaining custom logic is project-specific rather than a disguised copy of the standard capability;
   - the evidence names the manifest, API, documentation, or repository source that proves the fit.

   Classify each entry as one of:

   - `REUSE`: an existing dependency, helper, generated surface, platform API, or standard-library feature already owns it;
   - `ADOPT`: a verified external candidate is a better owner and would add a dependency;
   - `KEEP CUSTOM`: the behavior is project-specific or the candidate fails a stated constraint;
   - `OPEN`: the evidence is insufficient for a decision.

   Completion criterion: every reported finding passes the full gate, and every rejected candidate has a stated reason for `KEEP CUSTOM` or `OPEN`.

7. Lead with one verdict and write a spacious plain-text report. Keep the verdict, outcome, audit surface, and sources in short opening lines. Give every capability one numbered block with a decision label and a short title, then explain it in separate paragraphs. Put a blank line between every paragraph and every capability. Use plain text only: labels and numbered blocks, with no table, heading marker, or fenced block.

   VERDICT: REUSE | ADOPT | KEEP CUSTOM | MIXED | OPEN

   OUTCOME: <observable behavior>

   AUDIT SURFACE: <files, proposal, or diff point>

   SOURCES CHECKED: <manifest paths and platform, framework, or primary-source paths>

   CAPABILITY 1: REUSE
   Retry and backoff at src/client.rs:42

   Current
   <what the code owns>

   Preferred owner
   <dependency, platform API, framework, or standard-library feature>

   Why
   <coverage match and duplicated semantics, caller homework, or concrete failure surface>

   Change
   <the owner correction, or none>

   Evidence
   <manifest path and direct primary-source path or link>

   Custom remainder
   <project-specific part, or none>

   CAPABILITY 2: KEEP CUSTOM
   Tenant authorization at src/auth.rs:18

   <short explanation of why the behavior is project-owned>

   NEXT ACTION: <reuse, evaluate the new dependency, keep the custom layer, or gather the named evidence>

   Completion criterion: the report contains one calibrated verdict, one spaced block per capability, every reuse or adoption decision with evidence, the custom remainder, and the next action.

</what-to-do>

<supporting-info>

Existence is not fit. A package with a similar name is not a replacement until its documented semantics and the project's constraints line up. A new dependency can be a sound option without making current custom code a defect; an already-declared owner is stronger evidence because the project has already accepted its integration boundary.

</supporting-info>

## Boundary with library-fit

<what-to-do>

When no implementation exists and the main task is choosing one library, a combination, or custom work, use `$library-fit` for the pre-build decision and carry its coverage map into this audit. When code or a diff exists, complete this audit even when `$library-fit` was not invoked.

</what-to-do>
