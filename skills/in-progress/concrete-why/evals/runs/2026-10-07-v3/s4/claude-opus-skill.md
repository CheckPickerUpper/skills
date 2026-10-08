Closing an issue in v3.2 takes it off the release gate. The release stays blocked while any v3.2 issue is open, so leaving all four open blocks v3.2 on all four. That's the actual cost of leaving them open, and I should have said it first. The four don't all come out the same, though, and I'm changing my earlier plan: two should be closed as done, one is a live bug I shouldn't close, and one needs your decision.

My last two answers weren't reasons. "They're stale," "keeps the tracker clean," "reflects reality" and "no real benefit" are labels. "Stale" was also wrong for [#401](https://github.com/CheckPickerUpper/tasklist-app/issues/401): I reproduced that bug on `main` today.

**What closing does on GitHub**

- It marks the issue closed with a reason: "completed" or "not planned."
- It removes the issue from the open list and from v3.2's open count. That count is what blocks the release.
- Nothing is deleted. Anyone can reopen it.

**Done, but still open: [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) and [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)**

- CSV export shipped in v2.3 through [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455).
- The typo was fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470).
- Neither PR's description mentioned its issue. GitHub only closes an issue automatically when the PR says something like "Closes #402," so both stayed open.

If they stay open:
1. v3.2 can't release, even though neither issue has any work left.
2. The tracker says CSV export doesn't exist and the typo is still there, though both have shipped.

Closing them as completed, with a comment linking the PR that did the work, removes both blocks.

**A real bug, not stale: [#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)**

It's labelled `bug`, low priority, and nobody has touched it in 8 months. Here's what happens on `main` today:
1. Dark mode is on and the app starts cold.
2. The screen flashes white for about 150ms before the dark theme appears.

If I closed it as stale, the bug would still ship and the tracker would stop showing it. Your rule is that a bug ends fixed, or closed as won't-fix only by your decision. So I won't close it. Low-priority bugs have a 7-day deadline, and this one is far past it.

My recommendation is to fix it now, in its own PR with a regression test, before v3.2 ships. Leaving it open in v3.2 blocks the release until that fix lands. I don't recommend moving it out of the milestone to get around that: the white flash would ship in v3.2 anyway.

**A bug current builds can't hit: [#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)**

1. v3.0 raised `minSdkVersion` (the oldest Android version the app will install on) to 29, which is Android 10.
2. So Android 9 phones can't install any build from v3.0 onward, v3.2 included.
3. A crash that only happens on Android 9 can't happen in anything v3.2 ships.

Leaving it open blocks v3.2 on a crash no v3.2 user can hit. The right way to close it is "not planned": Android 9 is no longer supported. That's a won't-fix, so the decision is yours, not mine. Until you make it, the issue stays open and keeps blocking the release.

**What I couldn't confirm**

- Whether #403's crash was only on Android 9 or also happens on Android 10 and later. The title says Android 9 and I didn't test it anywhere else. If it does happen on newer versions, it's a live bug and needs a fix, not a close.
- Whether Android 9 users still on v2.x builds hit this crash. Closing the issue changes nothing for them either way.

**What decides it:** does the behaviour the issue describes still happen in what v3.2 ships? If not (#402, #404, and #403 if you drop Android 9), closing it unblocks the release. If it does (#401), closing it hides a bug that still ships.
