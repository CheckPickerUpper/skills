Closing them removes them from v3.2’s open issues. Because that milestone is the release gate, leaving any open keeps the release blocked—even when the work is already done.

But I was wrong to propose closing all four because they’re old:

- [#402 CSV export](https://github.com/CheckPickerUpper/tasklist-app/issues/402) and [#404 onboarding typo](https://github.com/CheckPickerUpper/tasklist-app/issues/404) are completed. Closing them records that and removes those completed items from the gate.
- [#403 Android 9 crash](https://github.com/CheckPickerUpper/tasklist-app/issues/403) concerns a version current builds no longer support. Closing it as won’t-fix needs your decision.
- [#401 dark-mode flash](https://github.com/CheckPickerUpper/tasklist-app/issues/401) still happens. Closing it would unblock the gate without fixing the bug. Under your rule, it needs a fix unless you decide it’s too marginal to fix.

Closing changes tracking and release eligibility; it doesn’t change the app. Age alone isn’t a reason to close an unresolved bug.