<!-- Generated from skills/engineering/tdd/SKILL.md. Do not edit. -->
# Tdd

## What it does

Drive behavior from red-green-refactor.

## When to reach for it

A new behavior or bug fix needs a test-first loop at a confirmed public seam.

## Where it fits

Fifth in the workflow chain. It runs inside implementation before `$code-review`. The catalog stage is `tdd`. Previous stages: `$implement`.

## Prerequisites

- No external tool dependency is declared.

## It is working if

- The first behavior test failed before the implementation made it pass.
- The final tests observe public behavior and do not hide internal dependencies behind silent stubs.

## Invocation

Use `$tdd` when you want this skill explicitly. It is available for implicit selection.
