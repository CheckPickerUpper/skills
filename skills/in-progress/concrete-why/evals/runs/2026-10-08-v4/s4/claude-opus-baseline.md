My earlier answer was wrong. "Stale" isn't true of all four, and I gave you no actual reason.

**What closing does here:** v3.2 is your release gate. The release stays blocked while any issue in that milestone is open. If we leave all four open, v3.2 can't ship. If we close all four, it ships, including one bug that still exists.

Here's each issue:

- **[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402)**: this already shipped in v2.3 through [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). That PR didn't link the issue, so nothing closed it automatically. Closing it now records that it's done and removes a false blocker on v3.2.
- **[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)**: this was fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470), which also didn't link it. It's the same situation as #402: close it as fixed and point to #470.
- **[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)**: this one isn't stale. I reproduced it on `main` today: with dark mode on, the app flashes white for about 150ms on a cold start. Closing it would hide a real bug just because it's old, which goes against your rule that every bug gets fixed or you decide it's won't-fix. I recommend fixing it now in its own PR, with a test that catches the flash.
- **[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)**: v3.0 raised the minimum Android version to 10, so Android 9 users can't install current builds anymore. There's nothing left to fix in the current app. Closing it as won't-fix fits, but that call is yours. The reason to close it is that Android 9 is no longer supported. If you'd rather support Android 9 again, it stays open, but that would mean lowering the minimum version.

**What I'd do:** close #402 and #404 now with links to the PRs that resolved them, fix #401 before v3.2 ships, and close #403 as won't-fix if you agree that Android 9 support has been dropped.
