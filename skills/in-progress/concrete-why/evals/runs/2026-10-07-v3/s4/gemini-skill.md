Leaving these issues open blocks the v3.2 release, because the milestone v3.2 serves as the release gate and won't allow a release while any issue inside it remains open. However, because one issue is a real bug, my earlier recommendation to close it was a default, not an argument. Close the three that are already solved, and decide whether to fix or won't-fix the remaining bug.

**The three already solved: #402, #403, and #404**

These issues are already resolved in the codebase but remain open in the v3.2 milestone, which acts as the release gate for the v3.2 release:
- [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) is a feature that already shipped in v2.3 via PR [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455).
- [#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) is a bug for Android 9, but v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 users can no longer install current builds.
- [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) is a bug that was fixed by PR [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470).

*What leaving them open does:*
1. The v3.2 release process checks the v3.2 milestone.
2. It finds #402, #403, and #404 still open.
3. The v3.2 release is blocked, waiting for work that is already done or no longer possible.

*What closing them does:*
Closing them removes them from the open milestone count, allowing the v3.2 release to proceed.

**The active bug: #401**

[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) is a low-priority bug in the v3.2 milestone. I reproduced it on `main` today: there is a ~150ms white flash on cold start when dark mode is on.

*What closing it as stale does:*
It drops the bug from the milestone and closes it without a fix. I have no concrete reason to close it this way. My earlier recommendation was a default, not an argument. You have a standing rule for this repository that every bug ends fixed or closed as won't-fix by your decision, with no bug backlog.

*What leaving it open does:*
1. The v3.2 release process checks the v3.2 milestone.
2. It finds #401 open.
3. The v3.2 release is blocked until you decide whether to fix the 150ms flash or close it as won't-fix.

**What decides it:** an open issue in a milestone blocks that milestone's release; close the ones where the work is already gone, and leave the real defect open until you make a decision.
