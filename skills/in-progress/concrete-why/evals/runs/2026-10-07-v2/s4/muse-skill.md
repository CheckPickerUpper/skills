**Short answer:** My earlier plan was wrong. Don't close all four as stale — close #402 and #404 because that work already shipped, keep #401 because it still reproduces, and #403 needs your won't-fix call.

My earlier lines — "they're old and keeping them open just adds noise" and "keeps the tracker clean... They're stale... no real benefit" — were labels, not reasons.

**[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) and [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404):** #402 is a feature request, #404 is a typo bug. #402 shipped in v2.3 via [PR #455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455) and #404 was fixed by [PR #470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470); neither PR referenced its issue, so both stayed open. Both sit in milestone v3.2, which blocks release while any issue in it is open.
- *If we close them:* they leave the v3.2 gate, so v3.2 stops waiting on work users already have.
- *If we leave them open in v3.2:* v3.2 stays blocked with nothing left to build — anyone checking the release sees two open items for a CSV export and a typo that are already in the app.

**[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401):** low-priority `bug`, last touched 8 months ago, but I reproduced it on `main` today: ~150ms white flash on cold start with dark mode on. It is also in v3.2.
- *If we close it as stale:* the tracker stops showing a bug that is still in current builds, so no session picks it up, and it violates your rule that every bug ends fixed or closed as won't-fix by your decision.
- *If we leave it open:* v3.2 stays blocked until it is fixed or you move it out of the gate. I have no concrete reason to close it.

**[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403):** `bug` for a crash on Android 9. v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 users cannot install current builds. It is also in v3.2.
- *If we leave it open in v3.2:* v3.2 stays blocked for a platform the app no longer installs on.
- *If we close it:* it has to be your won't-fix decision per your no-backlog rule, not a stale-close — closing as "stale" would imply it went away on its own, when the real consequence is you are dropping Android 9.

**What decides it:** whether a current install can still hit the issue — #402 and #404 cannot, #401 can, #403 cannot because those devices can't install the app.
