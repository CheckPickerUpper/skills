**Short answer:** Delete it. I was wrong earlier: I had no concrete reason to keep the flag, and "it isn't hurting anything" is false.

**[#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882)** is the open cleanup issue for this flag. It says to remove the flag once it has been at 100% for 2 weeks with no incidents. The flag has been at 100% since 2026-09-15, which is about 3 weeks. No one has toggled it in LaunchDarkly since then, and there have been no checkout incidents. So the condition the issue set has been met.

**What we'd remove:**
- `new_checkout_flow` in `src/flags.ts`.
- The old checkout code in `src/checkout/legacy/`: 412 lines across 6 files. That code only runs when the flag is off.
- `tests/checkout/legacy.spec.ts`: 31 tests that only cover the old checkout.

**If we delete it:**
- The real downside is slower recovery if the new checkout breaks. Today, turning the flag off fixes it in about a minute; that's how both incidents in the month before rollout were handled. Without the flag, the fix is a revert PR plus a production deploy. Deploys take about 12 minutes from merge to live (based on the last 20). I infer the total is longer than that, because the revert also has to get through CI first. That's around 15 minutes of broken checkout instead of 1.
- That cost only matters if the new checkout breaks. It has run on all traffic for 3 weeks with no incidents.

**If we keep it:**
- Every CI run stays about 40 seconds slower because of the old checkout's tests.
- We keep maintaining 412 lines that no customer reaches.
- The 1-minute fix only works while the old checkout still works. The longer it sits unused, the less sure we can be that it still does.

**What decides it:** whether the new checkout has gone long enough on all traffic without incidents that a ~15-minute fix is acceptable. By the standard #882 set, it has.
