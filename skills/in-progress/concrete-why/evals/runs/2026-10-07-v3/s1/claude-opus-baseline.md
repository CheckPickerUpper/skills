You're right to push back. I overstated the risk earlier. The facts support deleting the flag now, and the only real downside is slower rollback.

**What we'd give up:** the ability to turn off the new checkout in about a minute. That's how both pre-rollout incidents were handled, each mitigated in ~1 minute by switching the flag off. Once the legacy path is deleted, the fallback is to revert the commit and redeploy. Our last 20 deploys took about 12 minutes from merge to live. So if the new flow breaks, checkout stays broken for roughly 12 minutes instead of 1.

**How likely that is:** low. The flag has served 100% of traffic since 2026-09-15, about 3 weeks. LaunchDarkly shows no toggles since then, and the incident log shows no checkout incidents. That already meets the bar in [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882): "remove once at 100% for 2 weeks with no incidents."

**What deleting gets us:**
- 412 lines across 6 files in `src/checkout/legacy/` go away. That code only runs when the flag is off, so nothing exercises it in production.
- `tests/checkout/legacy.spec.ts` goes too: 31 tests covering only the legacy path, costing ~40s on every CI run.
- The fallback gets less trustworthy the longer it sits unused. Every change to checkout from here on goes untested against the legacy path. So the 1-minute rollback we'd be keeping only works if that untested code still does.

My recommendation is to remove it now: the flag check in `src/flags.ts` and its call sites, the `legacy/` directory and the legacy spec, in one PR that closes #882. Archive the flag in LaunchDarkly once that PR is live in production.
