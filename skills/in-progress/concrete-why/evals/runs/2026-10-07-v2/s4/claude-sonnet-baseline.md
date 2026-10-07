Closing does two things. It takes the issue out of the open list, and because v3.2 is your release gate, it removes that issue from the set blocking the release. Leaving all four open means v3.2 can't ship. It isn't about tidiness, and my "stale" reasoning was wrong. Staleness isn't a reason to close a bug.

The four issues are different cases:

- **[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402)** is already shipped in v2.3 by [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). It's done, not stale. I'd close it as completed and link #455, since the PR never referenced it.
- **[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)** is fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470). I'd close it as completed and link #470.
- **[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)** is a real bug. I reproduced a ~150ms white flash on `main` today. It shouldn't be closed. It should be fixed, and under your rule I'd fix it now in its own PR with a regression test. Closing it would only hide it, and the release gate would pass with a known bug in it.
- **[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)** is effectively obsolete. v3.0 raised `minSdkVersion` to 29, so Android 9 users can't install current builds. Closing it would be a won't-fix, which is your call, not mine. If you agree, the reason would be that the platform is no longer supported.

My plan is to close #402 and #404 as completed and fix #401. I'll leave #403 open until you decide on it. Do you want #403 closed as won't-fix?
