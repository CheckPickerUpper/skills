Delete it. The one concrete downside is that a checkout bug would take about 12 minutes to undo instead of about 1. My earlier "safety net, risky this soon" was a label, not a reason, and I've written out the actual cost below.

**What the flag does today**

`new_checkout_flow` (`src/flags.ts`, served by LaunchDarkly) has been at 100% of traffic since 2026-09-15. The old checkout in `src/checkout/legacy/` (412 lines across 6 files) only runs when the flag is off. That means nobody has run it in production for about 3 weeks.

**What deleting costs: the undo gets slower**

If a checkout bug shows up after the delete, the two ways to undo it compare like this:

*With the flag still there:*
1. Someone flips `new_checkout_flow` off in LaunchDarkly.
2. Customers are back on the old path in about 1 minute. That's the time-to-mitigate of both incidents in the month before rollout.

*With the legacy code deleted:*
1. Someone reverts the deletion commit and opens a PR.
2. CI runs, the PR merges, and the deploy takes about 12 minutes from merge to live (from the last 20 deploy runs).
3. Checkout stays broken for that whole time, plus however long steps 1 and 2 take.

Reverting would also not fix a bug in the new flow itself. It would only bring back the old path, and that path has had no production traffic since 2026-09-15, so I can't say it still works.

**Why that cost doesn't outweigh deleting**

- The rollback was used twice, both times before the rollout. There have been no checkout incidents since 2026-09-15.
- The cleanup trigger in [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) is "at 100% for 2 weeks with no incidents". It has been about 3 weeks, so the condition is met.
- Keeping the code has a recurring cost. `tests/checkout/legacy.spec.ts` has 31 tests that cover only the legacy path and add about 40 seconds to every CI run.

**What I couldn't confirm**

- Whether a traffic peak, such as a sale or holiday, is coming that the last 3 weeks didn't cover. If one is, waiting until after it is a reasonable call. I have no data either way.
- Whether anything outside `src/checkout/legacy/` and that one spec imports the legacy code. I only checked that it's reachable solely when the flag is off, so check that before deleting.
- How long a revert PR takes to get through CI and review. The 12 minutes covers only merge to live.

**What decides it:** the flag only saves you the difference between a 1-minute and a roughly 12-minute undo. That's worth paying while the new flow is unproven, and #882's own criteria say it's now proven.
