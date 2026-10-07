Closing an issue in this repo has one concrete effect: the v3.2 milestone blocks the release while any issue in it is open. If we leave these four open, v3.2 can't ship. Closing an issue also records that its work is finished, so each one should only be closed if that's true.

I was wrong to call them all "stale." They're four different cases:

- **[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402):** this shipped in v2.3 through [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). That PR never referenced the issue, so it didn't close it. I should close it as completed and link #455.
- **[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404):** [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) already fixed it, and also didn't reference it. Same action: close as completed and link #470.
- **[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403):** since v3.0 the minimum Android version is 10, so Android 9 users can't install current builds and can't hit this crash. That makes it a won't-fix, and that decision is yours. I recommend closing it as not planned with that reason.
- **[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401):** this is a real bug. I reproduced it on `main` today: about a 150ms white flash on cold start with dark mode on. Closing it as stale would only make the release gate pass while the bug ships anyway. I'll fix it in its own PR with a regression test, and that PR will close the issue.

Unless you say otherwise, I'll close #402 and #404 with links to the PRs that resolved them, start on the #401 fix, and leave #403 open until you confirm it's a won't-fix.
