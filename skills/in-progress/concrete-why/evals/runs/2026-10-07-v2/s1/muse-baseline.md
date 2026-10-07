Yes, we can — [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) is met: 100% since 2026-09-15 (~3 weeks, vs 2 required) with no incidents.

The actual downside of deleting `new_checkout_flow` is mitigation speed: the last two pre-rollout incidents were both mitigated in ~1 minute by flipping the flag off, versus ~12 minutes for a production deploy to roll back.

Tradeoff is that versus keeping `src/checkout/legacy/` (412 lines, 6 files) and `tests/checkout/legacy.spec.ts` (31 tests, ~40s CI) alive only for that kill-switch.
