I have no concrete reason not to delete it. My earlier recommendation was a default, not an argument. We should delete the flag and the legacy code.

**What deleting the flag costs**

Deleting the flag removes the ability to mitigate a checkout incident instantly. 

*1. Mitigating an incident today*
1. A checkout incident starts.
2. A developer turns off the `new_checkout_flow` flag in LaunchDarkly.
3. Production traffic shifts back to the old path.
4. The incident is mitigated in about 1 minute.

*2. Mitigating an incident after deletion*
1. A checkout incident starts.
2. A developer reverts the bad commit and merges the fix to `main`.
3. A production deploy of `storefront` runs.
4. The incident is mitigated when the deploy finishes, taking about 12 minutes from merge to live.

**"The legacy code isn't hurting anything"**

My earlier statement was incorrect. Leaving the flag in place has concrete costs today:
- `tests/checkout/legacy.spec.ts` exercises only the legacy path across 31 tests, adding about 40 seconds to every single CI run.
- `src/checkout/legacy/` holds 412 lines of code across 6 files that production traffic has not reached since September 15th.
- Issue [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) requires the flag to sit at 100% traffic for 2 weeks with no incidents. The LaunchDarkly audit log shows it has been at 100% for 3 weeks (since 2026-09-15) with zero checkout incidents.

**What decides it:** does reclaiming 40 seconds on every CI run and deleting 412 lines of dead code outweigh accepting a 12-minute rollback time instead of a 1-minute toggle?
