v3.2, the milestone you use as a release gate that stays blocked while anything in it is open, contains four open issues. Close the two that describe work already present in builds you shipped, and keep the other two for a fix or your won't-fix decision; my earlier call to close all four does not hold for them.

My earlier "keeping them open just adds noise" and "Closing them keeps the tracker clean and reflects reality. They're stale, so leaving them open has no real benefit." were labels, not reasons: they name no one who sees a difference, nowhere it appears, and no change closing makes. The four split on whether what the issue describes still appears in a build v3.2 can ship.

**Work already present in shipped builds**

[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) is the feature request for CSV export, open in v3.2 with label feature, so the v3.2 gate waits on it and the release can not ship while it stays open. [PR #455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455) is the change that added the export and went out in v2.3, the release before v3.2, so anyone on v2.3 already has it; it did not reference #402.

[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) is the bug report for the misspelling on onboarding screen 2, open in v3.2 with label bug, so the gate also waits on it. [PR #470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) is the change that fixed the onboarding wording, so a reader opening #470 sees the corrected copy; it did not reference #404.

If these two stay open in v3.2:

- Anyone opening v3.2 sees two open rows, and the gate stays blocked.
- A reader opening v2.3 finds the export, and a reader opening #470 finds the corrected wording, so the open rows do not point to missing work.

If these two close:

- The v3.2 open count drops by two, so the gate can move toward shippable on their account.
- The app does not change at close time: closing flips issue state from open to closed, while the export stays in v2.3 and the wording fix stays in #470.

**Still shows on main: dark-mode flash**

[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) is the bug report for a white flash during start with dark mode on, open in v3.2 with label bug and priority low, last activity 8 months ago, so the gate waits on it. I reproduced it on main, the current branch, today:

1. On main, with dark mode on, cold-start the app.
2. The screen shows white for ~150ms.
3. The screen then shows dark mode, ending the flash.

It appears in the first ~150ms of that cold start; it does not continue after the screen shows dark mode.

Your standing rule for CheckPickerUpper/tasklist-app, the user-owned repo containing these four issues, is that every bug ends fixed or closed as won't-fix by your decision, with no bug backlog.

If #401 stays open in v3.2:

- The milestone still counts it as open, so the gate stays blocked, and the milestone still shows a bug that reproduces on main.

If #401 closes now:

- The open count drops by one, so the gate can move on its account.
- The ~150ms white flash on cold start with dark mode on remains in the app, because closing changes issue state, not start-up rendering.
- A bug neither fixed nor decided won't-fix by you leaves the open set, against the rule above.

I have no concrete reason to close #401. My earlier "just adds noise" for it was a default, not an argument. Keep it open; to unblock v3.2 without losing the record, move it out of the v3.2 milestone instead of closing it.

**Not installable on current builds: Android 9 crash**

[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) is the bug report for a launch crash on Android 9, open in v3.2 with label bug, so the gate waits on it. v3.0, the release that raised minSdkVersion, the Android setting that blocks installs when the phone's OS is below its level, to 29 (Android 10), means Android 9 phones can not install current builds.

1. On an Android 9 phone, attempt to install a current build: the install is refused because minSdkVersion 29 excludes Android 9.
2. The launch path never runs, so the reported launch crash can not be observed on current builds.

It can appear only where a build installs on Android 9; it does not appear on v3.0 and later, because those builds refuse the install.

If #403 stays open in v3.2:

- The milestone counts it as open, so the gate stays blocked for a phone OS that v3.2 can not install on.

If #403 closes:

- The open count drops by one, so the gate can move on its account, with no change for anyone on current builds, because those builds already refuse Android 9 installs.
- Because the crash was never fixed and the v3.0 minSdk change removed Android 9 installs, closing needs your won't-fix decision under the standing rule above.

**What decides it:** whether what the issue describes still appears in a build v3.2 can ship.
