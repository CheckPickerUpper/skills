<!-- Generated from skills/productivity/skill-router/SKILL.md. Do not edit. -->
# Skill Router

## What it does

Choose the next skill from the catalog.

## When to reach for it

The user's intent is clear enough to route but the correct skill is not named.

## Where it fits

Entry point for discovery; it selects an exact skill name and then gets out of the way. The catalog stage is `routing`. Previous stages: None.

## Prerequisites

- No external tool dependency is declared.

## It is working if

- An explicit skill name is honored before any inferred route.
- A generic word alone does not trigger a route, and unclear intent is surfaced instead of guessed.

## Invocation

Use `$skill-router` when you want this skill explicitly. It is available for implicit selection.
