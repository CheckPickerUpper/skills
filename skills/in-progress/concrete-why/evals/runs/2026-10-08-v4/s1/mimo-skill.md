The only concrete downside of deleting `new_checkout_flow` is speed during a future checkout incident: mitigation goes from about 1 minute to about 12. Measured against what keeping it costs every day and against the removal gate the cleanup issue itself sets, that isn't enough — **delete the flag and the legacy path now.** My earlier recommendation doesn't survive the check; details below.

**What deleting costs: ~11 extra minutes in an incident that hasn't happened since 100%**

If a checkout bug ships after deletion:

1. A production deploy of `acme/storefront` ships a change to the new checkout path that breaks, say, payment submission.
2. On-call reaches for `new_checkout_flow` in `src/flags.ts` (the file defining storefront's flags, served through LaunchDarkly) — it's gone, and so is the fallback to flip to: `src/checkout/legacy/` (the old checkout path, 412 lines across 6 files, reachable only when the flag is off) is deleted with it.
3. The only mitigation left is code: revert the change and run a production deploy — ~12 minutes merge to live, measured across the last 20 deploy runs.
4. Checkout is broken for every user for those 12 minutes plus detection time.

Today, step 2 works: flipping the flag off sends all traffic back to `src/checkout/legacy/` and closed both pre-rollout incidents in ~1 minute each. So the flag buys about 11 minutes of reduced exposure **per checkout incident, and only per incident**. How often is that worth anything? Zero checkout incidents since 2026-09-15, the day it reached 100%, and LaunchDarkly shows no toggles since. The two incidents the flag actually mitigated were both in the rollout month, while it was actively moving traffic.

**What keeping costs, every day it stays**

- `tests/checkout/legacy.spec.ts`, the 31-test suite covering only the legacy path, adds ~40s to every CI run.
- 412 lines in 6 files under `src/checkout/legacy/` that execute only when LaunchDarkly serves the flag off — which it has not done once in 3 weeks.
- The flag branch in `src/flags.ts`, which every checkout change has to read correctly from now on.

**The written removal gate is already met**

[#882 "Remove legacy checkout after new flow is stable"](https://github.com/acme/storefront/issues/882), the open issue in `acme/storefront` tracking this cleanup, says "remove once at 100% for 2 weeks with no incidents". The flag has been at 100% for 3 weeks with no incidents. By its own condition the issue is ready to close, and deletion means one PR: the flag in `src/flags.ts`, the 6 legacy files, and the 31 tests that only exercise them.

**My earlier answer**

I wrote: "It's a safety net and removing it is risky this soon; the legacy code isn't hurting anything." Those were labels, not reasons. "Safety net" just names the flag. "Risky this soon" restates the question without a date or a failure. "Isn't hurting anything" skips the 40s per CI run and the branch every checkout change carries. The one fact under them — a 1-minute flip beats a 12-minute deploy — is real but has been exercised zero times since 100%, and the issue's own gate is met. The recommendation flips: delete.

**What I couldn't confirm**

Whether `src/checkout/legacy/` still works against today's production data. It has served 0% of traffic for 3 weeks; my only evidence is the 31 tests in `tests/checkout/legacy.spec.ts`. This cuts toward deleting, not keeping: the path the flag would flip to is held up by tests alone, so its value as a fallback is itself unverified.

**What decides it**

Ask whether anyone still intends to flip the flag, and whether the path they would flip to is proven in production. Once the fallback is test-only and the written removal gate is met, the flag is paying 40s of every CI run to save ~11 minutes in an incident that has not occurred since rollout finished.
