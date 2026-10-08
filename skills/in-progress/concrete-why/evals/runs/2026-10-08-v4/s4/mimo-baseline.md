Closing does three concrete things and nothing more:

1. Marks the issue `closed` in GitHub. It drops out of default open-issue views and out of the v3.2 release gate — that gate only counts open issues, so a closed issue stops blocking the release.
2. Records a reason on the issue timeline: who closed it, when, and (if we do it right) a comment linking the evidence — the PR that fixed it or the decision that made it moot.
3. Does **not**** delete anything. The issue stays searchable, readable, and reopenable if the decision turns out wrong.

So "leaving them open" isn't neutral — each open issue in v3.2 is actively holding the v3.2 release. That's the real cost, not noise.

But your question exposes that my earlier plan was wrong: I said "close all four as stale," and stale is not a valid reason under your rule (bugs end fixed, or won't-fix by your decision). Per issue:

- **#402, #404** — already **fixed**. Closing just records what happened: link PR #455 / PR #470 in a comment and close. No decision needed.
- **#403** — **won't-fix** by product decision: v3.0 raised minSdkVersion to 29, so Android 9 is out of scope. That's your call to confirm, then close with that reason.
- **#401** — **not fixed and not moot**: I reproduced the white flash on `main` today. Closing it would be hiding a live bug, and I won't do that without you explicitly saying won't-fix. It should either get fixed or get your won't-fix decision.

Want me to close #402/#404 with the PR links, and do you call #403 as won't-fix? And #401 — fix it, or is it won't-fix too?
