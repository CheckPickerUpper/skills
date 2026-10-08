You are right; my previous response was wrong. The downsides of keeping the flag are:

- **Slower CI:** `tests/checkout/legacy.spec.ts` wastes ~40 seconds on every CI run.
- **Dead code:** We are carrying 412 lines of unused code across 6 files in `src/checkout/legacy/`.
- **False safety:** The legacy code hasn't handled production traffic in 3 weeks. Flipping the flag off now would fail over to unexercised code, which is riskier than relying on the 12-minute deploy for a forward fix.
- **Ignored requirements:** Issue #882 explicitly requires removal after 2 weeks at 100% with no incidents. It has been 3 weeks.

I will remove `new_checkout_flow` from `src/flags.ts`, delete the legacy checkout directory and tests, and close #882.
