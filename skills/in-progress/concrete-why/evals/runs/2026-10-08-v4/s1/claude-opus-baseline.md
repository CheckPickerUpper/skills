I was wrong earlier: you should delete it. The flag already meets the condition your own issue set, and the one real downside is small.

**The downside:** if the new checkout breaks, rolling back gets slower. Today you flip the flag off in LaunchDarkly and it takes effect in about a minute. That's how both incidents in the month before rollout were fixed, at about 1 minute each. Once the flag and the legacy code are gone, rolling back means reverting the change in git and deploying. Your last 20 deploys took about 12 minutes from merge to live, so a checkout outage would last about 12 minutes instead of 1.

**Why that's worth accepting now:**
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) says to remove it "once at 100% for 2 weeks with no incidents." The flag has been at 100% since 2026-09-15, about 3 weeks.
- There have been no checkout incidents since then. The LaunchDarkly audit log shows nobody has toggled the flag off, even briefly.
- Keeping it isn't free. `tests/checkout/legacy.spec.ts` has 31 tests that only exercise `src/checkout/legacy/` (412 lines across 6 files). That code only runs when the flag is off, and those tests add about 40 seconds to every CI run.

So the trade is a slower rollback for a failure that hasn't happened in 3 weeks, in exchange for less code and faster CI on every run from now on.

**What the removal covers:** I'd do it as one PR that closes #882. It would:
- delete `src/checkout/legacy/` and `tests/checkout/legacy.spec.ts`
- remove `new_checkout_flow` from `src/flags.ts` and make the new flow the only path
- archive the flag in LaunchDarkly once the PR is live
