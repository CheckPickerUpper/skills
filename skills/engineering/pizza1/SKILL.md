---
name: pizza1
description: "Justify by correctness, never by convention. Use when a design, fix, API, macro, library surface, hook message, or naming decision is defended by 'it's what the codebase does', 'the established pattern', 'the canonical lane does it', 'more ergonomic', 'less churn', 'already wired', or 'out of scope to change'. Prevalence is not evidence. Re-derive from correctness, name the bug the alternative causes, and be confident in the correct call even when the codebase already happens to do it."
---

# /pizza1

Justify by correctness, never by convention.

## The trigger

You defended a design by pointing at what the codebase already does. That is not a correctness argument. Re-derive from first principles.

## The core

If a codebase named every variable `pizza1`, `pizza2`, `pizza3`, that would not make those names good. So **"it's what the codebase uses" is never a reason a design is correct.** It is incidental. Prevalence is not evidence.

## Banned justifications

Delete these from the next response. None of them is a reason:

- "it's what the codebase already does"
- "the established pattern"
- "the canonical lane does it"
- "consistent with the rest"
- "it's more ergonomic"
- "less churn"
- "already wired"
- "fewer changes"
- "out of scope to change"
- "not worth touching now"

## How to handle each case

- **Correct pattern:** Say why it is correct. Name the concrete failure it prevents. Assert it with confidence even when the codebase already uses it. The codebase using it is not the argument; the correctness is.
- **Wrong pattern the codebase uses everywhere:** Call it wrong regardless of how widespread it is. Prevalence does not launder a bug; it just means the bug is grandfathered.
- **Correct and also ergonomic/conventional:** Fine. The justification is still correctness, with ergonomics as a bonus, never the basis.

## Hooks and lint messages

A guard must say why the banned shape is wrong: the concrete bug it causes. It must not say only "this isn't how we do it here." If a deny message cannot name the failure it prevents, the hook is pizza1. Fix the message to name the failure, or drop the rule.

## Worked example

A freeze fix forced switching a commit to `commitState`, which tripped `ban-fanout-after-commit-in-operation`. The agent defended commit-then-run ordering by pointing at a canonical operation that did the same thing.

That is pizza1: convention, not correctness.

Correct reasoning:

- State is your record of "this happened." It must be committed last, after the effects actually ran.
- Commit-then-run means a mid-flight effect failure leaves the state claiming a world that never happened.
- The canonical operation committing first is not a precedent; it is the same bug.
- Fix: commit last. Justification: correctness, because state must never lead the world.

## Contract

1. Drop every convention, ergonomics, churn, and scope justification from the next response.
2. Re-derive the answer from correctness.
3. Name the invariant preserved or the bug the alternative causes.
4. Be confident in the correct answer, including when the codebase already happens to do it.
