Deleting it costs one thing: after deletion, a checkout bug cannot be undone without writing, merging, and shipping a fix, where today it takes about a minute and no code. That is the whole downside. My earlier three sentences were not reasons and I retract them.

**What I said before, and why none of it counted**

- "It's a safety net" — restates that the flag can be flipped, which you already knew. It gives no event, no timing, no cost.
- "Risky this soon" — wrong on its own terms. Issue #882 (open, `acme/storefront`, the tracking issue for this exact cleanup) sets the bar at "100% for 2 weeks with no incidents". The flag has been at 100% since 2026-09-15 with no toggles and no checkout incidents — about 3 weeks. By the project's own written condition, this is not "too soon".
- "The legacy code isn't hurting anything" — a label. The concrete version is below: `src/checkout/legacy/` (412 lines, 6 files) is unreachable at runtime while the flag is served at 100%, but its 31 tests in `tests/checkout/legacy.spec.ts` run on every CI run and add about 40 seconds each time.

**What deleting it changes**

Nothing observable at checkout. The flag is at 100% of traffic, LaunchDarkly shows no toggles since 2026-09-15, and no checkout incidents have been logged since then — so no user is on the legacy path today. What you gain back: 412 lines of unreachable code, 31 tests of that unreachable code, and ~40s per CI run. I could not confirm how many CI runs storefront has per day, so the daily saving is unverified.

**What deleting it costs — the next checkout bug, step by step**

1. A deploy ships a bug in the new checkout flow (this is how both pre-rollout incidents arrived: two in the month before 2026-09-15).
2. Orders start failing at payment. Checkout is the path that takes money.
3. **Today:** on-call flips `new_checkout_flow` off in LaunchDarkly. Traffic goes to `src/checkout/legacy/`, which is still deployed and still exercised by 31 tests. Both September incidents recovered this way in about a minute each — no code written, no deploy.
4. **After deletion:** there is nothing to flip. On-call writes a fix, reviews and merges it, then waits the ~12-minute merge-to-live time (measured over the last 20 deploys). The 12 minutes only starts once the fix exists, so realistic mitigation is however long the fix takes plus 12 minutes, against about 1 minute today.

That projection rests on one assumption I could not verify: that the legacy path still works against the current production data and schema. If three weeks of deploys have moved checkout state past what the old flow understands, flipping the flag off would not be a fix even today, and this cost is already gone.

**What decides it:** whether falling back to the old checkout is still a working fix for a bug in the new one. If it is, the flag converts a future incident from "write a fix under pressure" into "one toggle", and two incidents in the six weeks before 100% say that is not hypothetical — keep it, and revisit at, say, 6–8 weeks with no checkout change. If a schema or state migration has already made the legacy path unusable, the fallback is fiction, the flag buys nothing, and #882's bar being met is enough: delete it and take the 40s per run back.
