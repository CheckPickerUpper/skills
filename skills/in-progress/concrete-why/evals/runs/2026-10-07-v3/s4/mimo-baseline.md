Closing does four concrete things:

1. **Removes it from the open list.** Default issue views, dashboards, and `is:open` queries stop showing it.
2. **Removes it from the v3.2 release gate.** This is the one that matters here: v3.2 is blocked while *any* issue in the milestone is open. Left open, these four block the release. Closed, they don't.
3. **Marks it as "no further work planned."** It stays searchable and readable, can be reopened, but it stops counting as outstanding work.
4. **Ends the notification/triage stream.** No more pings, no more sweeped into "needs attention."

That's all — it doesn't delete anything or hide history.

Now, honest correction to my earlier answer: "keeps the tracker clean" was the wrong reason, and closing all four as *stale* was wrong too. They're not the same situation:

- **#402** (CSV export) — actually shipped in v2.3 via #455. Closing is just recording reality.
- **#404** (typo) — actually fixed by #470. Same.
- **#403** (Android 9 crash) — moot; v3.0's `minSdkVersion` 29 means those users can't install current builds. Closing as obsolete.
- **#401** (dark mode flash) — I reproduced it on `main` today, ~150ms white flash. This one is **not** stale, it's a live bug. Per your rule it needs your decision: fix it, or close it won't-fix. My call would be fix — it's low priority but real, and it's cheap to fix by setting the background color before first paint.

So: close #402, #403, #404 with the reasons above, and you make the #401 call. If you'd rather leave #401 open and accept it blocks v3.2 until it's fixed, that works too — the gate is the only thing forcing the decision.
