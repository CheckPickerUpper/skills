Turning off `new_checkout_flow`, the LaunchDarkly flag in `src/flags.ts` that selects the checkout path for storefront traffic, currently restores the legacy checkout without a deploy. Deleting it removes that roughly one-minute mitigation option; I’d still delete it now, because the agreed cleanup condition has been met.

The concrete downside is the time to restore the old path if the new checkout has a problem:

1. In the month before rollout, two checkout incidents occurred.
2. In each incident, turning the flag off restored the legacy path and mitigated the incident in about one minute.
3. After deleting the flag and legacy code, that action is unavailable. Restoring the old path would require a code rollback or restoration and a production deploy.
4. The last 20 storefront deploys took about 12 minutes from merge to live. Preparing the restoration could add time; I cannot give a verified total.

Those incidents show that the switch has helped before. They do not establish that another incident will occur, or that either previous problem remains.

Keeping the switch also keeps `src/checkout/legacy/`, the old checkout implementation used only when the flag is off: 412 lines across six files. Its dedicated suite, `tests/checkout/legacy.spec.ts`, runs 31 tests against that path and adds about 40 seconds to every CI run. Deleting both removes that code and recurring test time.

[Remove legacy checkout after new flow is stable (#882)](https://github.com/acme/storefront/issues/882), the open issue governing this cleanup, says to remove it after two weeks at 100% traffic with no incidents. The flag has served 100% since September 15, about three weeks, with no toggles and no checkout incidents since then.

My earlier “safety net” meant the faster mitigation described above. “Risky this soon” was not supported by the agreed threshold, and “the legacy code isn’t hurting anything” overlooked the CI cost. I’m changing my recommendation: delete the flag, legacy path, and legacy-only tests.

I cannot confirm how long a future rollback would take end to end or whether it would resolve a future incident. No source snippets are included because the supplied record contains verified facts but no exact code lines.

The deciding fact is whether retaining the roughly one-minute switch still justifies keeping the old implementation after the agreed stability period; the evidence here supports completing the cleanup.