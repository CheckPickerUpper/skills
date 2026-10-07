<what-to-do>
**Short answer:** Delete all three together — the flag, `src/checkout/legacy/`, and `tests/checkout/legacy.spec.ts`. My earlier "it's a safety net, removing it is risky" was labels without a number; the number is about 11 minutes, and I don't think it beats what keeping costs every day. They're one unit: a flag you can flip only mitigates anything while the old path it re-enables still exists, so keeping the flag alone buys nothing.

**If we delete:**
- The next checkout incident gets mitigated by a fix or revert deploy: ~12 minutes merge-to-live (last 20 deploy runs of `acme/storefront`) instead of ~1 minute flipping `new_checkout_flow` off in LaunchDarkly — the way both pre-rollout incidents were handled. That's ~11 extra minutes of broken checkout **per incident that happens**, and the incident log shows zero since 2026-09-15.
- Every CI run gets ~40s faster (`tests/checkout/legacy.spec.ts`, 31 tests covering only the legacy path), and 412 lines across 6 files that no live code path can reach leave `src/checkout/legacy/`.

**If we keep:**
- Every CI run keeps paying those ~40s forever, plus 412 lines stay maintained whenever checkout changes.
- What that buys: ~11 minutes off mitigation of a *future* checkout incident — contingent on one happening at all.
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882), the open issue tracking exactly this cleanup, sets the bar as "at 100% for 2 weeks with no incidents." It's been 100% since 2026-09-15 with no LaunchDarkly toggles and no incidents — 3 weeks. Waiting past the stated bar means the bar wasn't the reason to wait.

**What decides it:** whether `new_checkout_flow` will ever be flipped off again. If you can't name a realistic incident where it is flipped and the legacy path carries real traffic, the kit's 11 minutes is a discount you'll never collect, while the 40s per CI run is charged on every run.
</what-to-do>
