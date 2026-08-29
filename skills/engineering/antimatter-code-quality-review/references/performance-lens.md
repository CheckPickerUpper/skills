# Performance lens

This is where severity theater is easiest to commit. "That is quadratic" sounds like a finding at every size, including sizes where it is free. Refute harder here than anywhere else.

## The bar a performance finding must clear

State all three. A finding missing any one of them is destroyed.

1. **The operation.** Which call, on which collection.
2. **What grows.** Name the quantity and show that it grows: rows from a query, entities in a world, items a player holds, retries in a queue. A collection with a fixed small ceiling does not grow, whatever its shape.
3. **How often the path runs.** Once at startup, once per request, or every frame. The same operation is free in the first and fatal in the third.

If you cannot name a growing quantity, or the path runs once, the finding is destroyed. Report nothing.

## Direction one — the structure does not fit the operation

The `after` is a different data structure, not a faster loop. Ask what the code asks of the collection, then name the structure that answers it in one step.

| The code does this repeatedly | The structure it wanted |
|---|---|
| scans a list to find one item by a key | a map keyed by that key |
| checks whether an item is already present | a set |
| scans to find the smallest or nearest-due item | a heap, or a sorted structure |
| iterates one collection inside a loop over another | an index built once before the loop |
| sorts to answer a question about one element | a single pass |

A nested loop over the same collection is the loudest of these and the easiest to miss, because each loop reads as ordinary on its own line.

## Direction two — the work repeats and the answer does not change

A value computed inside a loop, from inputs the loop never touches, is computed once too many times. The `after` hoists it, or the structure carries it.

The same shape at a larger scale: a value derived on every read that changes only on write. Deriving on write and storing it moves the cost to the rarer event.

## Direction three — the path allocates every time it runs

A fresh collection, closure, or copy is free once and expensive on a path that repeats. Three that recur:

- **Rebuilding a collection to add one element.** Appending by copying the whole thing costs the whole thing every time, so adding n elements costs n squared. The `after` is a structure that appends in place, or one that does not need the intermediate copy.
- **A closure created per call** where one created once would serve every call.
- **A defensive copy of a value the caller already owns** and does not mutate.

Name what the allocation is per: per call, per element, per frame. An allocation with no repeating path is not a finding.

## Behavior-preservation

Usually easy, and say so explicitly: the operation returns the same answer by a different route. Two cases where it does not, and both must be stated rather than assumed:

- **Iteration order changes.** A map or set may not preserve insertion order. If anything downstream depends on order, the change is not behaviour-preserving.
- **Sharing replaces copying.** Removing a defensive copy is only safe when no one mutates the value. Prove it or keep the copy.

## Do not pendulum

A map for four elements is slower than the scan it replaced, and harder to read. A finding needs the growing quantity from the bar above; without it, the simple structure is the correct one and there is nothing to report.

Micro-optimisation is not this lens. Loop unrolling, operator swaps, and cached field reads change constants. This lens changes the shape of the cost.
