Leaving them open blocks the v3.2 release. Because the v3.2 milestone is a release gate, the app cannot ship while any issue in it remains open.

Closing them does the following:
- **#402 and #404:** Unblocks the release for work you already finished. #402 was shipped in PR #455, and #404 was fixed in PR #470.
- **#403:** Clears a bug that is no longer possible to hit. The crash is on Android 9, but v3.0 raised the minimum requirement to Android 10.

I was wrong to suggest closing **#401** (the dark mode flicker) as stale. I reproduced the 150ms flash today, so it is a real bug. Because your standing rule is that every bug must end fixed or closed as won't-fix with no backlog, leaving it open blocks v3.2 until it is fixed. You need to decide whether to fix it now or close it as won't-fix.
