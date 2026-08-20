<!-- Generated from skills/engineering/implement/SKILL.md. Do not edit. -->
# Implement

## What it does

Implement an approved ticket slice.

## When to reach for it

An approved spec or unblocked ticket has clear acceptance criteria and is ready to build.

## Where it fits

Fourth in the workflow chain. It coordinates `$tdd` during implementation and hands the finished diff to `$code-review`. The catalog stage is `implementation`. Previous stages: `$to-tickets`.

## Prerequisites

- No external tool dependency is declared.

## It is working if

- The requested slice works through its public seam and satisfies its acceptance criteria.
- Type checks and focused tests run during the work, with the full suite run before handoff.

## Invocation

Use `$implement` when you want this skill explicitly. It is explicit-only.
