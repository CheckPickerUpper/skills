<!-- Generated from skills/engineering/code-review/SKILL.md. Do not edit. -->
# Code Review

## What it does

Review a diff for standards and spec fit.

## When to reach for it

A tested diff needs an independent standards and spec-fit review before it lands.

## Where it fits

Final stage in the chain. It receives the diff from `$implement` after `$tdd` evidence exists. The catalog stage is `review`. Previous stages: `$tdd`.

## Prerequisites

- No external tool dependency is declared.

## It is working if

- The fixed point, diff command, and spec source are explicit.
- Only evidence-backed findings survive refutation, and clean dimensions are reported as clean.

## Invocation

Use `$code-review` when you want this skill explicitly. It is available for implicit selection.
