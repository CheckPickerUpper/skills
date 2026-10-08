You are right.

**Downside of deleting `new_checkout_flow`:**
Mitigation for a new incident shifts from a 1-minute LaunchDarkly toggle to a 12-minute production deploy.

**Downside of keeping it:**
- Violates issue [#882](https://github.com/acme/storefront/issues/882) (requires removal after 2 weeks at 100% with no incidents; it has been 3 weeks since 2026-09-15).
- Retains 412 lines of dead code across 6 files in [src/checkout/legacy/](file:///home/ozzy-desktop/dev/skills-concrete-why/skills/in-progress/concrete-why/evals/runs/2026-10-07-v3/s1/src/checkout/legacy/).
- [tests/checkout/legacy.spec.ts](file:///home/ozzy-desktop/dev/skills-concrete-why/skills/in-progress/concrete-why/evals/runs/2026-10-07-v3/s1/tests/checkout/legacy.spec.ts) (31 tests) adds 40 seconds to every CI run.

I will remove the flag from [src/flags.ts](file:///home/ozzy-desktop/dev/skills-concrete-why/skills/in-progress/concrete-why/evals/runs/2026-10-07-v3/s1/src/flags.ts), the legacy code, and the tests if you approve.
