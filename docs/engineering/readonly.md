<!-- Generated from skills/engineering/readonly/SKILL.md. Do not edit. -->
# Readonly

## What it does

Evidence-first read-only investigation.

## When to reach for it

The user wants an answer proved from available evidence without mutations.

## Where it fits

Use as a modifier before planning or implementation when the current state must stay frozen. The catalog stage is `investigation`. Previous stages: None.

## Prerequisites

- No external tool dependency is declared.

## It is working if

- The answer cites the checked files and commands.
- The final status proves no mutation occurred.

## Invocation

Use `$readonly` when you want this skill explicitly. It is explicit-only.
