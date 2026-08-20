---
name: tdd
description: "Use test-driven development at agreed public seams: write a failing behavior test, make the smallest change that passes, then verify the refactor. Use when building a feature or fixing a bug test-first, or when the work mentions red-green-refactor."
short_description: "Drive behavior from red-green-refactor."
allow_implicit_invocation: true
openai:
  interface:
    default_prompt: "Use $tdd to drive this change through a red-green-refactor loop."
    icon_small: "./assets/icon-small.svg"
    icon_large: "./assets/icon-large.svg"
    brand_color: "#EA580C"
  policy:
    products:
      - "codex"
catalog:
  stage: "tdd"
  order: 5
  aliases:
    - "test-driven development"
    - "red green refactor"
    - "write the test first"
  predecessors:
    - "implement"
  when: "A new behavior or bug fix needs a test-first loop at a confirmed public seam."
  where_it_fits: "Fifth in the workflow chain. It runs inside implementation before `$code-review`."
  success_signals:
    - "The first behavior test failed before the implementation made it pass."
    - "The final tests observe public behavior and do not hide internal dependencies behind silent stubs."
---

# Test behavior first

<what-to-do>

1. Name the public seam and read the project test runner, factories, fixtures, and relevant call sites before writing a test.
2. Write a test for one observable behavior. Use plain Given/When/Then language and an independent expected result. For a bug, make the test reproduce the bug first.
3. Run it and record the RED result. If it passes before the implementation changes, fix the test because it is not proving the new behavior.
4. Make the smallest implementation change that produces GREEN. Keep internal dependencies real; stub only external effects and record the boundary and reason.
5. Run GREEN again, then refactor without changing behavior and run the test again. Use near-miss negative cases when the behavior is a guard or router.
6. Report the seam, RED/GREEN/REFACTOR evidence, focused command, and any boundary stub before returning to `$implement` or `$code-review`.

</what-to-do>

<supporting-info>

The loop protects the behavior contract. A test that only checks an implementation detail or a far-away negative example can stay green while the real behavior breaks.

</supporting-info>
