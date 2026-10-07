**Short answer:** Yes — delete it. I was wrong to say keep it. My earlier “safety net” and “risky this soon” and “isn't hurting anything” were labels, not reasons.

**[#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882):** open cleanup issue; its body says remove once at 100% for 2 weeks with no incidents. That condition is met: `new_checkout_flow` in `src/flags.ts`, the LaunchDarkly flag that chooses which checkout code runs, has been at 100% since 2026-09-15 (about 3 weeks) with no toggles and no checkout incidents since.

*If we delete:*
- `src/checkout/legacy/` — the 6-file, 412-line checkout path that only runs when the flag is off — goes away, so the next person editing checkout reads one path.
- `tests/checkout/legacy.spec.ts` — the 31 tests that only exercise that path — goes away, so every CI run finishes ~40s earlier.
- We lose the 1-minute mitigation used in the two pre-rollout incidents, where flipping the flag off restored checkout. The next new-flow break would need a code revert plus a production deploy, which takes ~12 minutes merge-to-live from the last 20 runs, so checkout stays broken ~11 minutes longer.

*If we don’t:*
- We keep paying the ~40s on every CI run and keep the 412 lines to read around.
- We keep the 1-minute flag-off option for the next break.

**What decides it:** #882’s own test — 2 weeks at 100% with no incidents — is already passed, so the ongoing CI and code cost is certain and the faster-recovery benefit is only conditional.
