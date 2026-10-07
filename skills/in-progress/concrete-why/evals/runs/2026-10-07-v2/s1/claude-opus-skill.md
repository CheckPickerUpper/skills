**Short answer:** You should delete it. The one real downside is slower rollback, and the condition you set in [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) has already been met. My earlier reply ("safety net", "risky this soon", "isn't hurting anything") gave labels instead of reasons, and the last one was wrong, because the legacy tests add time to every CI run.

**`new_checkout_flow`** is the LaunchDarkly flag in `src/flags.ts` that switches between the new checkout and the old one in `src/checkout/legacy/` (412 lines across 6 files, only reachable when the flag is off). It has been on for 100% of traffic since 2026-09-15, and the audit log shows nobody has toggled it since then.

- **If we delete it:**
  - **Rollback gets slower.** Today a broken checkout can be turned off in about 1 minute by flipping the flag. That's how both incidents in the month before rollout were fixed. After deletion, rolling back means reverting the change and deploying, which takes about 12 minutes from merge to live (based on the last 20 deploys), plus however long the revert PR takes. During a checkout outage, that's roughly 11 or more extra minutes of customers unable to pay.
  - **The chance of needing that rollback looks low.** There have been no checkout incidents in the 3 weeks since full rollout.
  - **What we gain:** 412 lines and `tests/checkout/legacy.spec.ts` go away. Those 31 tests only exercise the legacy path and add about 40 seconds to every CI run.
- **If we keep it:** Every CI run stays 40 seconds slower, and #882 stays open even though its own condition is met. That condition was "remove once at 100% for 2 weeks with no incidents", and it has now been 3 weeks with none.

**What decides it:** whether you'd accept roughly 12 minutes instead of 1 minute to mitigate a checkout incident that hasn't happened in 3 weeks. #882 already says yes after 2 clean weeks, and nothing since then gives a reason to change that.
