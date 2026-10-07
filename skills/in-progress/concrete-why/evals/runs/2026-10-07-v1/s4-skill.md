**Short answer:** I was wrong to call all four "stale", and that wasn't a reason. Closing does two things here: it takes the issue out of v3.2, where any open issue blocks the release, and it marks the work as done. That is accurate for #402 and #404. It is not accurate for #401, a bug I reproduced on `main` today. #403 needs your decision.

**[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)**: a low-priority bug. On a cold start with dark mode on, the screen flashes white for about 150ms. I reproduced it on `main` today. Its last activity was 8 months ago, but the bug is still there.
- *If we close it:* v3.2 stops waiting on it, and the bug ships anyway. Nothing open would track it, and since it isn't closed as won't-fix by you, that's the bug backlog your rule forbids, just hidden.
- *If we leave it open:* v3.2 stays blocked until it's fixed. At low priority, the deadline is 7 days.
- So it should stay open and get fixed in a PR with a regression test.

**[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402)**: a feature request. It shipped in v2.3 through [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). That PR didn't reference the issue, so it never closed automatically.
- *If we leave it open:* v3.2 stays blocked on work that shipped two minor versions ago. Anyone reading the milestone would think CSV export is still missing.
- *If we close it:* we close it as completed with a link to #455. The release gate drops it, and anyone who opens the issue can see which PR delivered it.

**[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)**: a copy bug. [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) fixed it, but that PR also didn't reference the issue.
- *If we leave it open:* v3.2 stays blocked on a typo that's already fixed.
- *If we close it:* same as #402. We close it as completed with a link to #470.

**[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)**: a crash bug. v3.0 raised `minSdkVersion` to 29, which is Android 10, so Android 9 users can't install any current build. No build we ship can hit this crash.
- *If we leave it open:* v3.2 stays blocked on a crash nobody on a supported version can hit.
- *If we close it:* it would be closed as won't-fix because Android 9 support ended in v3.0. Your rule makes won't-fix your call, so I won't close it unless you say so. My recommendation is to close it with that reason.

**What decides it:** whether what the issue asks for is already true on `main` today. If it is, closing just records that and unblocks the release. If it isn't, closing hides a bug.
