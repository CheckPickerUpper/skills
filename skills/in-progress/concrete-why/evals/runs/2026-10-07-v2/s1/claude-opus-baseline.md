You're right to push back. I was wrong earlier: the cleanup condition is met, so I'd remove the flag now.

**The one real downside: slower recovery if the new checkout breaks.**
- **Now:** turning the flag off fixes checkout in about 1 minute. It did that for both incidents in the month before rollout.
- **After removal:** recovery means reverting the change and redeploying, which takes about 12 minutes from merge to live (going by the last 20 deploys). Checkout would stay broken for roughly 11 more minutes per incident.

**Why that risk is small:**
- The new flow has served all traffic since 2026-09-15, about 3 weeks, with no checkout incidents. Nobody has turned the flag off since then (LaunchDarkly audit log).
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) says to remove it "once at 100% for 2 weeks with no incidents". It has been 3 weeks with none.

**What keeping it costs.** I was also wrong that the legacy code isn't hurting anything:
- `tests/checkout/legacy.spec.ts` runs 31 tests against a path no customer reaches. They add about 40 seconds to every CI run.
- `src/checkout/legacy/` is 412 lines across 6 files that only run when the flag is off. They still have to be kept up to date with every change to checkout.

If you agree, I'll open one PR that closes #882. It will delete `src/checkout/legacy/`, the flag check in `src/flags.ts` and `legacy.spec.ts`. Retire the flag in LaunchDarkly only after that PR is live in production.
