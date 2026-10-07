<what-to-do>
**Short answer:** Closing does one concrete thing here: it unblocks the v3.2 release. "v3.2" is the release gate — while any issue in it is open, the release can't ship, and all four sit in it. But I was wrong to call all four "stale": #401 still reproduces today, so it needs a fix or your explicit won't-fix call, not an automatic close. Close #402 and #404 now; #403 and #401 are your decisions.

**[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402)** and **[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)**: a CSV-export feature and an onboarding typo. Both already shipped — #402 in v2.3 via [PR #455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455), #404 via [PR #470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470). Neither PR referenced its issue, so the issues never got closed.
- *If left open:* the v3.2 release stays blocked on work that is already in users' hands.
- *If closed:* nothing changes in the code; the tracker stops claiming unfinished work. No cost.

**[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)**: a launch crash on Android 9. v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 users cannot install any current build — the crash can't occur on an installable build anymore.
- *If left open:* v3.2 stays blocked on a crash no current user can hit.
- *If closed as won't-fix:* the tracker stops claiming a bug, and the reason (minSdk 29) stays recorded in the issue. Per your standing rule — every bug ends fixed or closed as won't-fix **by your decision** — this is your call, not mine.

**[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)**: low-priority bug, 8 months of no activity — but I reproduced it on `main` today: a ~150ms white flash on cold start with dark mode on. "8 months old" was a label; the flash still happens on the code you'd ship in v3.2.
- *If left open:* v3.2 release stays blocked until this is fixed or you explicitly decide not to.
- *If closed as stale:* the flash ships to every dark-mode user on cold start, the tracker loses the only record of it (nobody has filed it in 8 months, so no second report is coming), and it's closed "stale" rather than won't-fix by your decision — which your rule doesn't allow.

**What decides it:** whether the issue still describes something true on current builds. Not true (already shipped, can't occur) → close it. Still true → fix it or make your won't-fix call. #402 and #404 fail the test, #403 fails it only because the OS floor moved, #401 passes it.
</what-to-do>
