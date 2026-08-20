---
name: implement
description: "Implement an approved spec or unblocked ticket slice, keeping the work inside its acceptance criteria and handing the result to test-driven development and review. Use when the user is ready to build from agreed work."
short_description: "Implement an approved ticket slice."
disable-model-invocation: true
openai:
  interface:
    default_prompt: "Use $implement to build the first unblocked slice from this spec."
    brand_color: "#16A34A"
  policy:
    products:
      - "codex"
catalog:
  stage: "implementation"
  order: 4
  aliases:
    - "implement the spec"
    - "build from the tickets"
    - "start the implementation"
  predecessors:
    - "to-tickets"
  when: "An approved spec or unblocked ticket has clear acceptance criteria and is ready to build."
  where_it_fits: "Fourth in the workflow chain. It coordinates `$tdd` during implementation and hands the finished diff to `$code-review`."
  success_signals:
    - "The requested slice works through its public seam and satisfies its acceptance criteria."
    - "Type checks and focused tests run during the work, with the full suite run before handoff."
---

# Implement the approved slice

<what-to-do>

1. Read the approved spec or ticket, its blockers, acceptance criteria, and the repository standards before editing.
2. Confirm the slice is unblocked. If a required decision or dependency is missing, stop at that boundary and report it instead of inventing scope.
3. Trace the public seam and call sites. Keep the change inside the stated outcome and preserve existing behavior outside it.
4. Use `$tdd` at the agreed seams. Run type checks and focused tests during the work, then run the full configured suite before handoff.
5. Reconcile the result against every acceptance criterion, including failure, empty, permission, and recovery paths that the ticket names.
6. Hand the complete diff to `$code-review` with the fixed point, spec source, commands run, and any explicit deviations.

</what-to-do>

<supporting-info>

Implementation is complete at the behavior boundary, not when the changed files look plausible. The review stage owns structural cleanup and spec-fit judgment after the tests establish the behavior.

</supporting-info>
