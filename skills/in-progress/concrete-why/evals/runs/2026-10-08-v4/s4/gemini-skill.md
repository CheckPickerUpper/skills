Leaving these issues open stops the v3.2 release from shipping, because the v3.2 milestone blocks releases while any issue inside it is open. However, closing #401 violates your standing rule, so my earlier recommendation was wrong. I will close #402, #403, and #404, and leave #401 open for your decision.

**Issues already solved or impossible (Close)**

[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) is a feature request shipped in v2.3 by PR [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455).
[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) is a bug fixed by PR [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470).
[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) is a bug that cannot happen on current builds, because v3.0 raised `minSdkVersion` to 29 (Android 10), preventing Android 9 users from installing the app.

**What leaving them open does**
1. You prepare the v3.2 release.
2. The release gate checks the v3.2 milestone.
3. The gate sees these issues are open and blocks the release.

Closing them removes them from the milestone so the release can ship.

**Issue still happening (Leave open)**

[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) is a low-priority bug in the v3.2 milestone that I reproduced on `main` today:
1. The user turns on dark mode.
2. The user cold starts the app.
3. The screen flashes white for ~150ms before the dark UI renders.

I have no concrete reason to close this. My earlier answers ("keeps the tracker clean", "reflects reality", "adds noise") were labels, not arguments. You have a standing rule that every bug ends fixed or closed as won't-fix by your explicit decision. Closing a bug that still happens, just because it is old, violates your rule. Leaving it open blocks the release, ensuring you either fix it or make a won't-fix decision before v3.2 ships.

**What decides it:** Does the issue describe a defect or missing feature that still happens on `main`?
