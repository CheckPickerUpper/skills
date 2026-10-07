I was wrong earlier. We should remove the flag now, because it has already met the bar written in [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882): "100% for 2 weeks with no incidents."

- **Time at 100%:** about 3 weeks, since 2026-09-15. The LaunchDarkly audit log shows no toggles since then.
- **Incidents since rollout:** none.

**The one real downside:** slower recovery if the new flow breaks. Today, flipping the flag off fixes checkout in about a minute; that's how both incidents in the month before rollout were fixed. After the flag is removed, recovery means reverting and deploying, which takes about 12 minutes based on the last 20 deploys. Removing it moves the worst case from about 1 minute to about 12.

**What keeping it costs:**
- **Legacy code:** 412 lines across 6 files in `src/checkout/legacy/`, which nothing reaches while the flag is on. Any checkout change has to keep working with that code, or it quietly drifts out of date.
- **Slower CI:** `tests/checkout/legacy.spec.ts` runs 31 tests that cover only that dead path, adding about 40s to every CI run.
- **A useful rollback?** Its value drops the longer the flag stays on: if the new flow fails months from now, the legacy code will have drifted and may not work when you switch back to it.

Three quiet weeks is good enough evidence that the 1-minute rollback is no longer worth those costs. If you agree, I'll remove the flag from `src/flags.ts`, delete `src/checkout/legacy/` and its test file, and open a PR that closes #882. The flag in LaunchDarkly can be archived after the PR is live.
