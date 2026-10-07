You're right, my earlier answers didn't say what closing does. "Stale" was the wrong reason, and one of the four isn't stale at all.

**What closing does here:** v3.2 is the release gate, and the release stays blocked while any issue in that milestone is open. Leaving an issue open is not neutral. It holds up v3.2. Closing one removes it from the gate, records why it closed (completed or not planned), and notifies the people subscribed to it.

**What each issue needs:**

| Issue | Actual state | Right action |
| --- | --- | --- |
| [#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) | Still a live bug. I reproduced it on `main` today: a ~150ms white flash on cold start with dark mode on. | Fix it. Closing it as stale would hide a real bug, and it should block v3.2 until it's fixed. |
| [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) | Shipped in v2.3 by [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). The PR never linked the issue, so it was never closed. | Close as completed with a link to #455. Right now it blocks v3.2 for work that's already done. |
| [#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) | Can't happen on current builds. v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 can't install them. | Close as won't fix because Android 9 is no longer supported. Closing a bug as won't fix is your call, not mine. |
| [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) | Fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470), which also never linked the issue. | Close as completed with a link to #470. |

So #402 and #404 are already done and should close today. #401 needs a fix before v3.2 ships. #403 needs your decision.

**Your call on #403:** I recommend closing it as won't fix because Android 9 has been unsupported since v3.0. If you'd rather keep it, it stays open in v3.2 and keeps blocking the release until Android 9 support comes back.
