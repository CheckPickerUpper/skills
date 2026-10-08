Fair push — "stale" isn't a reason. The concrete effect here is the v3.2 gate: while those 4 issues stay open in v3.2, v3.2 can't ship. Closing is what removes that block.

Per issue:

* [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) shipped in v2.3 by [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). Leaving it open blocks v3.2 for work that's already done.
* [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) was fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470). Same — leaving it open blocks v3.2 for a fix that's already in.
* [#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) still reproduces on `main` today — ~150ms white flash on cold start with dark mode on. Closing it wouldn't fix that, it would just hide a real bug. If you don't want it to block v3.2 we should move it out of the milestone, not close it as stale, unless you decide it's won't-fix.
* [#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) can't be fixed on the current builds — v3.0 raised `minSdkVersion` to 29, meaning the app only installs on Android 10+, so Android 9 users can't install it. Leaving it open blocks v3.2 for an unsupported platform. I propose won't-fix for that reason, but that's your call.

So my correction: close #402 and #404 as done, and keep #401 / #403 open until you decide won't-fix or move them out of v3.2.
