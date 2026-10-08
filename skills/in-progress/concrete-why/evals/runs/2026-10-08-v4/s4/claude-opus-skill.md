Closing an issue in v3.2 removes it from the list that blocks the v3.2 release, because v3.2 can't ship while any issue in it is open. If all four stay open, v3.2 can't ship. They don't all come out the same way, though. #401 is a live bug, and closing it would ship v3.2 with that bug still in it. I'm withdrawing my plan to close all four.

My earlier answers relied on two labels: "they're stale" and "keeps the tracker clean." Neither was a reason, and "stale" is wrong for #401.

**What leaving them open does**

The v3.2 milestone works as the release gate. While any issue in it is open, the release is blocked. All four issues are in v3.2. Leaving any of them open, for any reason, holds the release.

**[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) and [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404): already done, close as completed**

- **#402** is a feature request. [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455) shipped it in v2.3.
- **#404** is a bug. [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) fixed it.

Neither PR mentioned its issue, so GitHub never closed them automatically. Here's what each choice does:
- **Leave open:** v3.2 is blocked by work that has already shipped.
- **Close:** the release unblocks, and the tracker shows what's actually true. I'll link each issue to the PR that did the work when I close it.

**[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401): still a bug, don't close**

It's labelled `bug`, priority low, with no activity for 8 months. I reproduced it on `main` today:
1. Turn dark mode on.
2. Fully quit the app and start it again (a cold start).
3. The screen flashes white for about 150ms, then the dark theme appears.

Here's what each choice does:
- **Close it:** v3.2 ships with that flash, and the tracker says it's resolved when it isn't.
- **Leave it open:** v3.2 stays blocked until it's fixed.

Your rule is that every bug ends fixed or closed as won't-fix by your decision. Eight months without activity isn't a reason to close it. My recommendation is to fix it before v3.2, as a low-priority bug due within 7 days. If you'd rather not fix it, closing it as won't-fix is your call.

**[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403): your decision**

v3.0 raised the minimum Android version (`minSdkVersion`) to 29, which is Android 10. Android 9 users can't install current builds, so no build we ship can hit this crash. Here's what each choice does:
- **Leave it open:** v3.2 is blocked by a crash on a version we no longer ship to.
- **Close it:** the issue would close as "not planned," with the `minSdkVersion` change as the reason.

That's closing a bug without fixing it, which under your rule is your decision, not mine. Since Android 9 support has already been dropped, I recommend closing it.

**What I couldn't confirm:** I didn't check whether v3.2 contains other open issues besides these four. Closing these four may not be enough on its own to unblock the release.

**What decides it:** has the problem stopped happening in what we ship? #402 and #404 have, so close them. #403 can't happen in current builds, so it's yours to close. #401 still happens on `main`, so it stays open until it's fixed.
