The concrete downside is one thing: rollback speed.

- With the flag: if a latent bug surfaces in the new flow, mitigation is flipping `new_checkout_flow` off in LaunchDarkly — ~1 minute, as demonstrated twice in the month before rollout.
- Without it: mitigation is reverting and redeploying — ~12 minutes from merge to live, measured over the last 20 deploys. So a bad regression costs you roughly 11 extra minutes of live breakage, and during those 12 minutes there's no way to disable the new checkout at all.

That's it. Everything else is in favor of deleting:

- Issue #882's own exit criteria — 100% for 2 weeks with no incidents — are met: 3 weeks at 100%, no toggles, no checkout incidents since 2026-09-15. By the issue's own definition, this is due.
- Keeping it isn't free: 412 lines of reachable-only-when-off code that nobody has exercised in production for 3 weeks, 31 tests adding ~40s to every CI run, and a flag that will otherwise live forever.

So my "it's a safety net" answer was too vague — the safety net is worth about 11 minutes of mitigation time, and the issue you filed already agreed that trade expires after 2 stable weeks.

One caveat before deleting: the 3-week window proves the new flow survives normal traffic, not that the old path still works. If you want to keep the 1-minute rollback for a while longer, the honest version is "we're past #882's criteria but extending the window deliberately" — that should be a decision recorded in #882, not left implicit.

My recommendation: delete flag + `src/checkout/legacy/` + `tests/checkout/legacy.spec.ts` in one PR (they die together — the tests only cover the dead path), close #882 with a link to it. If you want a rollback path afterward, the revert of that merge serves the same purpose at the same ~12-minute cost as any other fix.
