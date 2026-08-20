<!-- Generated from skills/engineering/antimatter-code-quality-review/SKILL.md. Do not edit. -->
# Antimatter Code Quality Review

## What it does

Strict code-quality review with adversarial refutation.

## When to reach for it

A diff needs a structural review that reports only findings that survive refutation.

## Where it fits

Use after implementation when the review needs a correctness-first structural lens. The catalog stage is `review`. Previous stages: None.

## Prerequisites

- No external tool dependency is declared.

## It is working if

- Every finding has before-and-after evidence and a behavior-preservation basis.
- A clean diff receives an explicit approval instead of a manufactured finding.

## Invocation

Use `$antimatter-code-quality-review` when you want this skill explicitly. It is available for implicit selection.
