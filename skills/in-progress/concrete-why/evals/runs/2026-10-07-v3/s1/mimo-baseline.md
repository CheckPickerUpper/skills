Fair — the vague answer wasn't good enough. Here's the concrete downside:

**The flag is your fast rollback.** The two pre-rollout checkout incidents were both mitigated by flipping the flag off — about 1 minute each. If you delete the flag and `src/checkout/legacy/` together, your only mitigation for a checkout incident becomes a redeploy, which takes ~12 minutes from merge to live. That's roughly a 10x slower time-to-mitigate during exactly the incident where every minute costs conversions.

**What you actually pay to keep it:**
- `src/flags.ts` entry + LaunchDarkly serving (trivial)
- 412 lines / 6 files in `src/checkout/legacy/`
- 31 tests in `tests/checkout/legacy.spec.ts` (~40s per CI run)

**What you get:** the ~1-minute escape hatch above, and nothing else — the flag isn't protecting you from anything new, it's just preserving the old path as a tested fallback.

One thing worth flagging honestly: issue #882's own gate is "100% for 2 weeks with no incidents." You're at 3 weeks with no toggles and no incidents since 2026-09-15. By the bar the issue itself sets, it's eligible for removal *now* — so "this soon" in my earlier answer was wrong.

So it's a real tradeoff, not a clear hold:
- **Remove now** — meets #882's criteria, but you lose the fast rollback until the new flow has been through a real checkout incident or a high-traffic event (e.g. a sale) at 100%.
- **Keep a bit longer** — pay 40s CI and 412 lines, retain the 1-minute rollback until the new flow has survived one stressful period.

My actual recommendation: split it. Delete the legacy tests and the dead branch of the flag check first (kills the 40s CI cost), keep the flag as a kill-switch wired to a fail-safe for another few weeks, then remove the legacy path and flag once the new flow has been through a peak-traffic event. That's roughly what a staged cleanup would look like. But if you just want it gone, removing it now is defensible under #882's stated criteria — the honest cost is only the slower mitigation path.
