Leaving these four issues open blocks v3.2: that milestone is the release gate, and any open issue in it prevents release. Closing an issue removes that blocker; it does not fix the reported behaviour.

My earlier “keeps the tracker clean” and “they’re stale” were not reasons to close them. I retract the blanket recommendation.

- [#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) is a low-priority bug in v3.2 that still affects dark-mode users. I reproduced it on `main` today:
  1. A user has dark mode enabled.
  2. They cold-start the app.
  3. The screen flashes white for about 150ms.

  Closing it would unblock its part of the release gate while leaving that flash in place. Leave it open and fix it. Your standing rule permits closing an unfixed bug as won’t-fix only by your decision; eight months without activity does not supply that decision.

- [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) is a feature request in v3.2 whose capability already shipped in v2.3 through [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). [#404 Typo “recieve” in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) is a bug in the same milestone already fixed through [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470). Neither PR referenced its issue, so both issues stayed open. Close these as completed and record the corresponding PR in each issue’s body. Leaving them open blocks v3.2 on work already delivered.

- [#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) is a bug in v3.2 concerning Android 9 users. Current builds require Android 10 or newer because v3.0 raised `minSdkVersion` to 29. Closing it removes the release blocker, but does not establish that the crash was fixed: Android 9 users cannot install the current build. I recommend closing it as won’t-fix because current builds no longer support that version, but that decision belongs to you.

I could not confirm whether the Android 9 crash was fixed in older builds.

The deciding fact is whether the requested outcome was delivered, still needs fixing, or is something you explicitly choose not to fix—not how old the issue is.