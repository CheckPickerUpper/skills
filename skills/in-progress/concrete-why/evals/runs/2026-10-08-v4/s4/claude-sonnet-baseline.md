Closing an issue does two things: it takes the issue out of the open list, and it removes it from the v3.2 release gate. Release is blocked while any issue in v3.2 is open, so leaving all four open blocks the release. That is the only practical difference between open and closed.

My "they're stale" reasoning was wrong, because the four issues are in different states:

- **[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402):** This shipped in v2.3 via [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455), which never referenced the issue. It is done, so closing it just records that. I'd close it and link #455.
- **[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404):** [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) fixed it, and it also never referenced the issue. It is done, so I'd close it and link #470.
- **[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403):** v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 users can't install current builds. The crash can no longer happen on a supported device. Closing it means won't-fix, and under your rule that is your decision, not mine.
- **[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401):** This is not stale. I reproduced it on `main` today: a ~150ms white flash on cold start with dark mode on. Closing it would hide a real bug. Under your zero-bugs rule it should be fixed, or you should close it as won't-fix.

I'd close #402 and #404 now and fix #401 in its own PR with a regression test. That leaves #403 for you to decide. Once #401 is fixed and #403 is decided, v3.2 is unblocked.

Do you want to close #403 as won't-fix because Android 9 is no longer supported?
