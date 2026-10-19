---
"checkpickerupper-skills": patch
---

**`make-diagram`** now catches what readers objected to in diagrams the checker had passed.

`make-diagram` (model-invoked) now has the author read every word as a non-technical stranger before the first render, and draws only flows; rulebooks become tables.

- An arrow means the target waits on the source, so outputs produced independently branch side by side instead of being chained.
- Lanes hold only the steps that differ. A step both lanes take is drawn once in a shared flow, and the checker refuses a step drawn twice.
- A box row holds one item, and the checker refuses comma lists; use bullet rows.
- Every check states its exact condition, every branch what follows, and every end whether it can be retried. The checker refuses an end box that gives only its name.
- The checker refuses a diagram with no `<stem>.words.txt`, so the cold read of every word happens before the owner sees it.
- Levels, ranks and other states with move-up and drop rules go in a table. An arrow back to an earlier state is no longer an accepted judgment call.
