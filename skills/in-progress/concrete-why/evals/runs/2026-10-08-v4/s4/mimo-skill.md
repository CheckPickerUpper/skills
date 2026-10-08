Leaving them open keeps them counted against the v3.2 milestone, and v3.2 is the release gate: the release is blocked while any issue in that milestone is open. So "leave them open" doesn't just look untidy — it holds the release. But my earlier answers were labels, not reasons, and they were also wrong about which four to close. Splitting them:

**#402 Export task list to CSV** (label `feature`, in milestone v3.2) — **#404 Typo "recieve" in onboarding screen 2** (label `bug`, in milestone v3.2)

These two are already done. #402 shipped in v2.3 via PR #455 "Add CSV export"; #404 was fixed by PR #470 "Onboarding copy fixes". Both PRs merged without referencing their issue, so GitHub never auto-closed anything — that is the whole reason they are still open.

- Leaving them open: each one keeps counting as an open issue in v3.2, so the release gate stays red for work that is already shipped. The milestone then says the release is waiting on a CSV export that shipped in v2.3.
- Closing them: the issue stops counting against the gate, and the close is the record that the work landed. The issue text, the PRs, and any links stay readable either way.

**#401 Dark mode toggle flickers white on app load** (label `bug`, priority low, in milestone v3.2) — **#403 Crash on launch on Android 9** (label `bug`, in milestone v3.2)

These two are not stale, and I should not have grouped them with the others.

- #401 still fails today: I reproduced on `main` a ~150ms white flash on cold start with dark mode on. Leaving it open is accurate and blocks v3.2; closing it as "stale" would mark a live bug as done.
- #403 is unreachable on current builds: v3.0 raised `minSdkVersion` to 29, so Android 9 users can't install the app and can't hit the crash. But "we no longer ship to that OS" is your call to make, not mine to infer — your standing rule says every bug ends fixed or closed as won't-fix **by your decision**. So closing it needs you to say "won't-fix".

So the answer to "what does closing actually do": it removes the issue from the open set that the v3.2 gate counts, and it records why the work is finished — fixed (as for #402, #404) or won't-fix (as #403 would have to be). Opening and closing are also how the tracker answers "is this still true" later.

**What I couldn't confirm:** whether the release gate distinguishes close reasons (fixed vs. won't-fix) or only counts open issues in the milestone. I verified the blocking rule, not its implementation.

**What decides it:** closing is the tracker's record of "done or decided dead", and it's also the only state that stops an issue from holding the v3.2 gate — so an issue that is fixed or that you've decided to drop should close, and one that still reproduces stays open until it's fixed or you call it won't-fix.

Revised recommendation: close #402 and #404 as fixed now. Tell me for #403 whether "Android 9 can't install current builds" is your won't-fix — if yes I'll close it on that decision. #401 I leave open, unless you say won't-fix, because it reproduces today.
