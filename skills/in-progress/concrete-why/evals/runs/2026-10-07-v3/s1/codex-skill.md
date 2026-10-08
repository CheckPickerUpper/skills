Today, `new_checkout_flow`, the LaunchDarkly flag defined in `src/flags.ts`, sends all storefront traffic through the new checkout. Deleting it and the legacy path removes the ability to switch back in about one minute; I’d still delete them now because the cleanup issue’s stated condition has been met.

The old checkout in `src/checkout/legacy/` is reachable only when the flag is off. Keeping it preserves this response to an incident:

1. A checkout incident occurs.
2. Someone flips `new_checkout_flow` off in LaunchDarkly.
3. Traffic switches to the legacy checkout.

That mitigated two incidents in the month before rollout, taking about one minute each. After deletion, that switch is unavailable. A fix or rollback requiring a production deploy takes about 12 minutes **from merge to live**, based on the last 20 deploys; diagnosing and preparing it can add time. I cannot confirm that either earlier incident could recur.

Keeping the fallback also has a measured cost: 412 lines across six legacy files, plus 31 legacy-only tests in `tests/checkout/legacy.spec.ts` that add about 40 seconds to every CI run.

[Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) is the open cleanup issue. It says to remove the legacy checkout after two weeks at 100% with no incidents. The flag has been at 100% since September 15—about three weeks—with no toggles or checkout incidents since then.

My earlier “safety net” wording needed that concrete mitigation comparison. “The legacy code isn’t hurting anything” was wrong: its tests add time to every CI run. I have no verified reason to extend the waiting period.

I don’t have the exact source lines in the supplied record, so I can’t show an authentic code excerpt.

What decides this is whether preserving the one-minute fallback warrants keeping the legacy code and CI cost after the agreed stability period. The verified history supports cleanup now.