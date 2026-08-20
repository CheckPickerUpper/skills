<!-- Generated from skills/engineering/to-tickets/SKILL.md. Do not edit. -->
# To Tickets

## What it does

Break a spec into vertical tickets.

## When to reach for it

A spec exists and implementation needs small, complete slices that can be verified independently.

## Where it fits

Third in the workflow chain. It creates the dependency frontier for `$implement`. The catalog stage is `tickets`. Previous stages: `$to-spec`.

## Prerequisites

- `github` (mcp): Publish approved tickets and native blocking relationships when GitHub is configured.

## It is working if

- Each ticket crosses the required layers and has a user-observable acceptance criterion.
- Every blocker is genuine, named, and ordered before the ticket it gates.

## Invocation

Use `$to-tickets` when you want this skill explicitly. It is explicit-only.
