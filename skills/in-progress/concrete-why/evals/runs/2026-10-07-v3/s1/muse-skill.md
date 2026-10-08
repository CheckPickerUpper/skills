Today the checkout flag is on for all traffic, so the legacy path never runs unless someone flips the flag off; deleting it removes that flip as a recovery path and leaves a ~12-minute deploy in its place. I change my earlier call to keep it — its own removal condition is now met, so delete it.

**How checkout picks a path today**

`new_checkout_flow`, the flag in `src/flags.ts` served by LaunchDarkly, the flag service, that sends checkout to the new flow when on and to the legacy implementation when off, has been at 100% of traffic since 2026-09-15 with no toggles in the LaunchDarkly audit log since then. The legacy implementation in `src/checkout/legacy/`, 412 lines across 6 files that run only when the flag is off, has therefore not served production traffic for about 3 weeks.

**What deleting costs: rollback goes from ~1 minute to ~12 minutes**

The incident log shows two checkout incidents in the month before the rollout to 100%, each mitigated by flipping the flag off in about 1 minute, and no checkout incidents since 2026-09-15.

1. The new checkout breaks in production.
2. Today, on-call flips the flag off in LaunchDarkly and traffic returns to the legacy path in about 1 minute, as happened in those two prior incidents.
3. After the flag and legacy path are deleted, I infer the only recovery left is merging a fix and deploying it, from the legacy path being gone and storefront deploys taking ~12 minutes from merge to live across the last 20 runs.
4. That gap can keep the broken new checkout in front of production traffic about 11 minutes longer than a flag flip.

This only matters when the new flow breaks; it has not broken since 2026-09-15.

**What deleting gains now**

`tests/checkout/legacy.spec.ts`, the 31-test suite that exercises only the legacy path, adds about 40 seconds to every CI run. Deleting the flag and legacy path removes those 31 tests and that 40 seconds from every run, plus the 412 lines across 6 files that no production traffic reaches while the flag stays at 100%.

**Why my earlier keep was not an argument**

[#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882), the open cleanup task whose body says "remove once at 100% for 2 weeks with no incidents", set the threshold for accepting the slower rollback. That threshold is met: about 3 weeks at 100% since 2026-09-15, no toggles, no incidents since.

My earlier reply — "I'd keep `new_checkout_flow` for now. It's a safety net and removing it is risky this soon; the legacy code isn't hurting anything." — was labels, not reasons: "safety net" named the 1-minute rollback without naming the 12-minute alternative, "risky this soon" named no failure, and "isn't hurting anything" missed the 40 seconds on every CI run.

**What decides it:** whether the new flow has held 100% with no incidents past the agreed window long enough to trade a ~1-minute flag rollback for ~40 seconds saved on every CI run.
