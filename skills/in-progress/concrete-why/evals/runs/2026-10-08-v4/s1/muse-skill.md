Checkout has run 100% on the new flow since 2026-09-15 with no toggles and no incidents, past the 2-week bar set for removal. I have no concrete reason to wait — my earlier keep call was a default, not an argument; delete it.

**How checkout picks a path today**

`new_checkout_flow`, the flag that selects the new checkout instead of the legacy one in `acme/storefront`, the user-owned repo holding checkout, lives in `src/flags.ts`, the file that declares the flags LaunchDarkly serves, and is served by LaunchDarkly, the service that delivers flag values to the app. The flag has been at 100% of traffic since 2026-09-15, and the LaunchDarkly audit log shows no toggles since then. When the flag is off, checkout uses `src/checkout/legacy/`, the 412-line implementation across 6 files that is the only code reachable in the off position; at 100% on, that directory serves no traffic.

**What removal was waiting on**

[Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882), the open issue that gates deletion of the legacy path, says in its body "remove once at 100% for 2 weeks with no incidents". That condition is met: about 3 weeks at 100% since 2026-09-15 with no checkout incidents in the incident log, the record of checkout incidents, since then.

**What deleting costs — the downside you asked for**

The two checkout incidents in the month before rollout, the two entries in the incident log that both list a flag flip as the mitigation, each in ~1 minute, show what the flag does today:

1. A bug in the new checkout reaches checkout traffic.
2. Someone flips `new_checkout_flow` off in LaunchDarkly.
3. Checkout uses `src/checkout/legacy/` again.
4. The incident mitigates in ~1 minute.

After deletion, with the flag and `src/checkout/legacy/` gone:

1. The same new-flow bug reaches checkout traffic.
2. There is no flag to flip.
3. Mitigation needs a merge plus a production deploy of storefront, the merge-to-live path that took ~12 minutes across the last 20 runs.
4. Checkout traffic hitting the new flow during those ~12 minutes stays on the broken path.

So a future new-flow bug can keep checkout on the broken new flow for ~12 minutes instead of ~1 minute. That gap rests on the two prior ~1-minute flag mitigations and the last 20 deploy runs. It happens only if the new flow breaks; it has not happened since 2026-09-15.

**What keeping costs**

`tests/checkout/legacy.spec.ts`, the 31-test suite that exercises only the legacy path, runs on every CI run, the pipeline run that executes storefront's tests, and makes each run ~40s longer. The 6 files in `src/checkout/legacy/` remain in checkout while serving no traffic since 2026-09-15.

**My earlier keep line**

My earlier line — "I'd keep `new_checkout_flow` for now. It's a safety net and removing it is risky this soon; the legacy code isn't hurting anything." — was not a reason. "Safety net" and "risky this soon" named no event, no observer, and no time when waiting ends. "Isn't hurting anything" was wrong: the suite charges ~40s on every CI run.

**What I couldn't confirm:** I could not confirm whether anything outside checkout reads `new_checkout_flow`; the facts cover only that the legacy path is reachable solely when the flag is off. I infer the 1-minute vs 12-minute gap for a future bug from the two prior flag mitigations and the last 20 deploy runs, not from the content of those incidents, which I did not read.

**What decides it:** Once a flag has passed its agreed time at 100% with no incidents, waiting longer does not shrink the rollback gap deletion removes — it only keeps charging the test and review cost.
