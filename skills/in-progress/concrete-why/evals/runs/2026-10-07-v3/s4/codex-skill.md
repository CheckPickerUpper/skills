All four issues are in **v3.2**, whose release gate blocks the release while any issue remains open. Closing them removes those blockers; it does not change the app. My earlier “stale” and “keeps the tracker clean” explanations were not reasons to close them, and I withdraw the blanket recommendation.

The issues need different outcomes:

- **[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)** is a low-priority bug that still affects dark-mode users on `main`:
  1. A user with dark mode enabled starts the app cold.
  2. The screen flashes white for about 150ms.
  3. Dark mode then appears.

  Leaving it open in v3.2 keeps the release blocked by an unfixed bug. Closing it removes that blocker while users still see the flash. Its eight months without activity do not establish that it is fixed. **Fix it before closing**, unless you decide it is too marginal to fix and close it as won’t-fix. Your standing rule reserves that decision for you.

- **[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402)** requests a feature already shipped in v2.3 through [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). **[#404 Typo “recieve” in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)** reports an onboarding bug already fixed through [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470). Neither PR referenced its issue, so both remain open in v3.2.

  Leaving these open blocks v3.2 on work already delivered. **Close both as completed**, recording the corresponding PR in each issue body.

- **[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)** reports a bug on a platform current builds no longer support:
  1. An Android 9 user tries to install a current build.
  2. v3.0’s minimum Android version is Android 10.
  3. The user cannot install that build, so they cannot reach its launch screen.

  Leaving it open in v3.2 makes the current release wait on an Android 9 report. Closing it would remove that blocker, but **would not establish that the crash was fixed**. I could not confirm whether older installed builds still crash or whether they remain supported. Close it as won’t-fix only if you decide Android 9 no longer requires a fix.

The deciding fact is whether the requested work is delivered, still affects supported users, or has been explicitly declined—not how long the issue has been quiet.