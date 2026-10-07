Leaving them open blocks v3.2 — the milestone is the release gate, so while #401-#404 are in it, release stays blocked. Closing isn't just hygiene; it removes that block and stops signaling we intend to fix them in v3.2.

My earlier "close all as stale" was wrong. Checked against the code and history:

* [#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401): still reproduces on `main` today — ~150ms white flash on cold start with dark mode on. It's a real low-priority bug, not stale. Per your rule it ends fixed or closed as won't-fix by you, so I shouldn't close this. I can fix it now in its own PR with a regression test and keep it in v3.2.
* [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402): already shipped in v2.3 by [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455), which just didn't reference it. Close as completed and remove from v3.2.
* [#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403): v3.0 raised `minSdkVersion` to 29, so Android 9 can't install current builds. There's nothing to fix on supported versions. I propose closing this as won't-fix and removing from v3.2, but that's your decision — say the word and I'll close it.
* [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404): already fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470), which didn't reference it. Close as completed and remove from v3.2.

If you confirm: I'll fix #401, close #402 and #404 as done, and close #403 as won't-fix only after you approve, which unblocks v3.2.
