The specific downside is your recovery time if something goes wrong:

- **With the flag (now):** If checkout breaks, flipping the LaunchDarkly toggle restores the old path in **~1 minute** (as done in the two pre-rollout incidents).
- **Without the flag (deleted):** Mitigation requires merging a revert or fix and waiting through the **~12-minute** deployment pipeline.

That said, keeping it is not free:
- It maintains **412 lines** of dead code across 6 files in `src/checkout/legacy/`.
- `tests/checkout/legacy.spec.ts` runs 31 tests and adds **~40 seconds** to every CI run.
- It has been at 100% traffic with zero incidents for 3 weeks, meeting the exit criteria defined in issue #882 (2 weeks incident-free).

If you are comfortable trading the 1-minute flag kill-switch for standard 12-minute deploy-based rollbacks, we can proceed with removing it.
