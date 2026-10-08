Closing them removes them from the v3.2 release gate: **any open issue in that milestone blocks release.** It also records that the work is resolved or that you’ve decided not to fix it. Age alone justifies neither; my earlier answer was wrong.

These issues need different treatment:

- [#402 CSV export](https://github.com/CheckPickerUpper/tasklist-app/issues/402) and [#404 onboarding typo](https://github.com/CheckPickerUpper/tasklist-app/issues/404) are already shipped or fixed. Closing them records completion and removes false release blockers.
- [#403 Android 9 crash](https://github.com/CheckPickerUpper/tasklist-app/issues/403) concerns a version current builds no longer support. Closing as won’t-fix requires your decision to leave that old-version crash unresolved.
- [#401 dark-mode flash](https://github.com/CheckPickerUpper/tasklist-app/issues/401) still happens—I reproduced it today. Closing it would remove the release blocker while leaving the bug. Under your rule, I should fix it unless you decide it’s too marginal to fix.

Leaving all four open keeps v3.2 blocked, including by two completed items. Closing all four as stale would hide two unresolved decisions.