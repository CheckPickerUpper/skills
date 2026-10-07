**Short answer:** Closing them clears the v3.2 release gate. While any issue in that milestone is open, v3.2 can't ship. My earlier "they're stale" wasn't a reason, and it was wrong for #401, which still reproduces today. Three of the four should be closed. #401 needs a fix or your decision before v3.2 can ship.

**What leaving any of them open does:** v3.2 is your release gate, so any open issue in it blocks the release. If all four stay open, v3.2 doesn't ship.

**[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) and [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)** are already done. CSV export shipped in v2.3 through [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). The typo was fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470). Neither PR linked its issue, so neither issue closed when the PR merged.
- *If we close them* as completed with a link to the PR: v3.2 loses two blockers. Anyone reading the issue can see which PR did the work.
- *If we leave them open:* they block v3.2 even though there's no work left on them.

**[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403):** v3.0 raised the minimum to Android 10, so Android 9 phones can't install any current build. No current build can hit this crash.
- *If closed as won't-fix:* v3.2 loses a blocker. Nobody on a supported version is affected.
- *If left open:* it blocks v3.2 over a crash that can't happen on any build you ship.
- It's labelled `bug`, and closing a bug as won't-fix is your call, so I won't do it myself. I recommend closing it. The reason is "Android 9 isn't supported since v3.0."

**[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401):** a low-priority bug. I reproduced it on `main` today. With dark mode on, a cold start flashes white for about 150ms. "No activity for 8 months" didn't mean it was fixed.
- *If we close it:* dark-mode users keep seeing the flash, and nothing tracks the bug any more. That breaks your rule that every bug ends fixed or is closed as won't-fix by you.
- *If we leave it open:* v3.2 stays blocked until it's fixed. You could also move it out of v3.2, which unblocks the release but leaves the bug unfixed. My recommendation is to fix it now.

**What decides it:** whether the problem the issue describes still exists in a build you ship. #402 and #404 are fixed, and #403 can't happen on any build you ship, so they close. #401 still happens, so it stays open until it's fixed.
