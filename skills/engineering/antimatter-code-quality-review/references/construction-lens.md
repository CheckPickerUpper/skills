# Construction lens

A finding says the code is wrong. The upgrade says the wrong thing cannot be written. Take the upgrade whenever it is available: it retires the finding's whole class instead of the one instance, and it is the highest-value survivor a review produces.

## Procedure

1. **Locate the writer.** Find the code that creates the bad state. A reader, a crash, a failing consumer, a test that catches it: all evidence, none of them the writer.
2. **Name the bad state without the incident's words.** Strip the file name, the feature, the type, the local lifecycle word. State the invalid situation in words that survive those going away. If the restated sentence stops making sense, the incident still owns the finding.
3. **Find the earliest owner.** Walk up from the writer to the highest place that already knows the fact. A guard beside the writer is valid; a shape at the owner is better, because it removes the need for the guard.
4. **State what becomes unspellable.** Name the exact declaration a person could write today and could not write after. That sentence is the finding's `after`.
5. **Close the bypasses.** A blessed owner is evidence, not closure. If another writer can still reach the bad state, name it: the finding is not landed until every route is shut or the remaining ones are stated.

## The family this catches most often

A **redundant field**: a member whose value is already decided by the arm, kind, or type it sits on.

Three tells, any one of which is enough:

- Every arm of the union writes the same value for it.
- The constructor fixes it and the outcome copies it back out.
- Its type permits values the surrounding arm cannot mean.

The `after` is always deletion, and it is always behaviour-preserving when nothing reads the field. Check that first: a redundant field with a live reader is a different, larger finding.

## The evidence bar

A construction finding's `after` is a **shape**, not a check. "Validate this at the boundary" is the finding restated; "this arm no longer carries the field, so the contradiction has nowhere to be written" is the upgrade.

If the `after` you can write is a check rather than a shape, say so and report the finding at its own severity. A construction upgrade claimed and not delivered reads as a stronger finding than it is.

## Do not pendulum

Construction is precision, not a bigger type. A shape so tight it makes a legitimate state unspellable is its own defect, and it trains the next author to add an escape hatch beside it, which reopens every route. Leave the honest state reachable.
