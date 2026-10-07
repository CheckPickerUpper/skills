The only real downside is rollback speed.

- **With the flag:** if the new flow breaks checkout, flipping it off mitigates in ~1 minute (proven twice pre-rollout).
- **Without it:** you need a revert + prod deploy, and merge-to-live is ~12 minutes from the last 20 runs — so mitigation goes from ~1 min to ~12+ min, and that's assuming you've already diagnosed it and the revert merges cleanly.

That's the whole trade. There's no other cost to keeping it — but there's also no strong reason to keep it past the stated bar: #882 says "remove once at 100% for 2 weeks with no incidents," and it's been 100% since 2026-09-15 (~3 weeks) with zero checkout incidents and no audit-log toggles. The issue's own condition is already met, so my earlier "too soon" was more cautious than the evidence supports.

So the decision is really: **is a 1-minute rollback worth more to you than 12 minutes, right now?**

Delete now if:
- checkout isn't entering a risky window (launch, sale, big traffic spike)
- you're fine with 12-min mitigation if something regresses

Keep a bit longer if you have an upcoming event where an hour of broken checkout is expensive — that's the only scenario where the flag still earns its keep.

If you delete, do it as one change: `src/flags.ts` + `src/checkout/legacy/` (412 lines, 6 files) + `tests/checkout/legacy.spec.ts` (31 tests, ~40s/CI run), and remove the flag from LaunchDarkly so it doesn't linger as a stale flag. That also gets you ~40s off every CI run and closes #882 with its criteria documented as met.
