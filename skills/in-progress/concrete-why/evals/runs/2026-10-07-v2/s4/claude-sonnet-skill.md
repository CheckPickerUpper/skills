**Short answer:** Closing removes an issue from v3.2's open count, and that count is what blocks the release. My earlier answers ("stale", "noise", "reflects reality") were labels, not reasons. Age was never the reason. Checking each issue separately, I was wrong about #401, and #403 is your call.

**[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402)** (feature): [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455) already shipped it in v2.3, but that PR never referenced #402, so GitHub never closed it.
- *If we leave it open:* v3.2 stays blocked on a feature that already exists.
- *If we close it:* it no longer counts against the release gate, and the tracker says the feature exists. Nothing is lost.

**[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)** (bug): [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) fixed it but didn't reference #404.
- Same as #402. Leaving it open blocks the release for a bug that is already fixed. Closing it as completed loses nothing.

**[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)** (low-priority bug): I reproduced it on `main` today. With dark mode on, a cold start shows a ~150ms white flash.
- *If we close it:* a real bug disappears from the tracker, which breaks your rule that a bug ends fixed or closed as won't-fix by your decision. I shouldn't close it, and "it's 8 months old" doesn't justify it.
- *If we leave it open:* it keeps v3.2 blocked until it is fixed.
- I recommend fixing it, since it's a low-priority bug with a reproduction. If you'd rather accept the flash, closing it as won't-fix is your decision to make.

**[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)** (bug): v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 users can't install current builds.
- *If we leave it open:* it blocks v3.2 for a crash nobody can reach on a current build, and no fix is planned.
- *If we close it as won't-fix:* the tracker matches the v3.0 decision to drop Android 9.
- This is a bug, so closing it is your call. I propose won't-fix for the reason above.

**What decides it:** whether the issue still describes something wrong in the current code. #402 and #404 don't, because shipped PRs resolved them. #403 describes a case that v3.0 removed on purpose. #401 still reproduces.

I'll close #402 and #404 as completed now, and leave #401 and #403 open until you decide.
