Honestly, the downside is small, and I overstated it earlier. I'd delete it.

**What you lose:** the one-minute rollback. Both incidents before rollout were fixed by flipping the flag off in about a minute. Once the legacy path is gone, the same fix means reverting the removal and deploying, and a deploy takes about 12 minutes from merge to live. That's the whole risk: if a checkout bug turns up, mitigation goes from ~1 minute to ~12.

**Why that's worth accepting now:**
- The flag has been at 100% for about 3 weeks with no toggles and no checkout incidents.
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) says to remove it once the flag has been at 100% for 2 weeks with no incidents, and that bar is met.
- Keeping it isn't free. The legacy path is 412 lines across 6 files, and its 31 tests add ~40s to every CI run.
- The longer it stays, the less anyone remembers how the legacy path worked, so the safety net gets less useful over time.

**What I'd do:** delete `src/checkout/legacy/`, `tests/checkout/legacy.spec.ts`, and the `new_checkout_flow` check in `src/flags.ts`. Then archive the flag in LaunchDarkly after the deploy is live, not before. It stays served until the new code is out, so nothing changes mid-deploy. I'd put it in one PR that closes #882, so a revert is a single commit if something does go wrong.

Want me to go ahead and open that PR?
