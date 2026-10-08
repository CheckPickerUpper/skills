I have no concrete reason not to delete it. My earlier recommendation that keeping it is a "safety net" and "risky this soon" was a default, not an argument. You should remove the flag and the legacy code.

**What deleting the flag costs**

`new_checkout_flow` (the LaunchDarkly flag in `src/flags.ts` that routes traffic) currently takes about 1 minute to mitigate a checkout incident by flipping it off. Without the flag, mitigating an incident requires reverting the code and running a production deploy of `acme/storefront` (the repository), which takes about 12 minutes from merge to live.

**What keeping the flag costs**

[#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882), the open issue tracking the removal, requires the new flow to run at 100% traffic for 2 weeks with no incidents. It has been at 100% for 3 weeks (since 2026-09-15) with zero incidents.

While the flag remains:
- `tests/checkout/legacy.spec.ts` (31 tests that exercise only the legacy path) runs on every CI run, adding about 40 seconds to the build.
- `src/checkout/legacy/` keeps 412 lines across 6 files of old checkout code that are unreachable when the flag is on.

**What decides it:**
The new flow has met the issue's 2-week incident-free requirement, so the 40-second CI cost of testing unreachable code outweighs the lost 1-minute toggle mitigation.
