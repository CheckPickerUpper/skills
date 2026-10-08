Deleting is fine now. My earlier "risky this soon" was vaguer than the facts support.

**The only real downside is a slower rollback.**
- **Today:** if checkout breaks, you flip `new_checkout_flow` off in LaunchDarkly and it's fixed in about 1 minute. That's how both incidents in the month before rollout were handled.
- **After deletion:** the fix is a revert PR plus a deploy, which takes about 12 minutes from merge to live. A checkout outage would last roughly 12 times longer.

**Why that downside is small here:**
- The flag has been at 100% since 2026-09-15, about 3 weeks, with no toggles in the LaunchDarkly audit log.
- There have been no checkout incidents in that time.
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) asks for 2 weeks at 100% with no incidents, and that bar is already met.

**What you get from deleting:**
- 412 lines across 6 files in `src/checkout/legacy/` go away.
- The 31 tests in `tests/checkout/legacy.spec.ts` go away, which saves about 40s on every CI run.
- The flag stops being a branch every future checkout change has to consider.

**Recommendation:** delete it. If you want one more safeguard, wait until after your next high-traffic period. That's your call, since I don't know your traffic calendar. Otherwise I'll open a PR that removes the legacy directory, its tests, and the flag check in `src/flags.ts`, and closes #882. Afterwards the flag can be archived in LaunchDarkly.
