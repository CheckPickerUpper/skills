---
name: code-review
description: "Review a diff from a fixed point on two axes: documented repository standards and fit to the originating spec or ticket. Use for a branch, pull request, or work-in-progress after implementation and tests."
short_description: "Review a diff for standards and spec fit."
allow_implicit_invocation: true
openai:
  interface:
    default_prompt: "Use $code-review to review this diff for standards and spec fit."
    brand_color: "#DB2777"
  policy:
    products:
      - "codex"
catalog:
  stage: "review"
  order: 6
  aliases:
    - "review this diff"
    - "review the branch"
    - "pre-merge review"
  predecessors:
    - "tdd"
  when: "A tested diff needs an independent standards and spec-fit review before it lands."
  where_it_fits: "Final stage in the chain. It receives the diff from `$implement` after `$tdd` evidence exists."
  success_signals:
    - "The fixed point, diff command, and spec source are explicit."
    - "Only evidence-backed findings survive refutation, and clean dimensions are reported as clean."
---

# Review the finished diff

<what-to-do>

1. Pin the fixed point before reading the diff. Confirm the ref resolves, capture `git diff <fixed-point>...HEAD`, and record the commit range.
2. Find the originating spec or ticket and the repository standards. If no spec exists, say that spec-fit review is unavailable instead of guessing intent.
3. Review two independent axes: standards and spec fit. Widen beyond the diff only where a finding's blast radius requires it.
4. For every provisional finding, attempt to refute it. Keep a finding only when it has a concrete before/after, a named defect, behavior-preservation evidence, and a stated blast radius.
5. Report blocking findings, suggestions, clean dimensions, unavailable evidence, and the exact commands used. An empty or unresolved diff fails the review frame.
6. Return the verdict to `$implement` with the smallest next action for each surviving finding.

</what-to-do>

<supporting-info>

Strict review means high evidence, not high drama. A clean approval is a valid result; invented severity hides the defects that matter.

</supporting-info>
