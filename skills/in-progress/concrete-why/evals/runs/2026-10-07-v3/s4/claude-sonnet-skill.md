Closing an issue does one thing here: it takes the issue out of the open count on the v3.2 milestone, and v3.2 is your release gate. The release is blocked while any issue in it is open, so leaving all four open keeps v3.2 from shipping. That is the cost of leaving them open.

My earlier answers ("keeps the tracker clean", "no real benefit") were labels, not reasons, and they hid that the four issues are different. Two are done, one is moot, and one is a live bug I shouldn't have called stale.

**Already done: close them**
- [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) is a `feature`. [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455) shipped it in v2.3 but never referenced the issue, so GitHub never closed it. Leaving it open blocks the release for work that has already shipped.
- [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) was fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470), which also never referenced it. Same situation.

Closing these two just makes GitHub's state match what the code already does.

**Android 9 crash: your decision**
[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) is a `bug`. v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 users can't install current builds. The crash can't happen on anything you ship now. The only reason I can see to close it is that it can no longer happen on a current build. Under your rule, closing a bug as won't-fix is your call, not mine, so I'm proposing it, not doing it.

**Dark mode flicker: leave it open**
[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) is a `bug` with low priority, and it has had no activity for 8 months. Earlier today I reproduced it on `main`: a white flash of about 150ms on cold start with dark mode on. A bug that still reproduces isn't stale, so I was wrong to include it. Closing it would also close the bug without fixing it, which your rule reserves for you.

Because it is in v3.2, it blocks the release. You have three ways forward:
1. Fix it before releasing.
2. Move it out of v3.2 to a later milestone.
3. Close it as won't-fix yourself.

**What I couldn't confirm**
- I haven't checked whether anyone is still running an older build on Android 9. That is the only thing that would make #403 matter.
- I confirmed #455 and #470 from their titles and the issue labels, not by diffing them against the issues' exact wording.

**What decides it:** an issue is closed only if its work has shipped or can no longer happen. Age doesn't count. #402 and #404 qualify, #403 qualifies if you accept it as won't-fix, and #401 doesn't.

I'll close #402 and #404 now, unless you tell me otherwise. #401 and #403 wait for your decision.
