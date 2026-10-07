Closing an issue removes it from the open work count. Here, that has a concrete effect: **v3.2 cannot release while any issue in its milestone is open.** Closing all four would clear that gate, even though one bug still reproduces. It would not fix anything in the app.

My “stale” explanation was wrong. These need different decisions:

- [CSV export](https://github.com/CheckPickerUpper/tasklist-app/issues/402) and the [onboarding typo](https://github.com/CheckPickerUpper/tasklist-app/issues/404) are already resolved. Closing them records completed work.
- [Android 9 launch crash](https://github.com/CheckPickerUpper/tasklist-app/issues/403) needs a support decision: current builds require Android 10, but that doesn’t establish that the old crash was fixed.
- [Dark-mode white flash](https://github.com/CheckPickerUpper/tasklist-app/issues/401) still happens. Leaving it open accurately records unfinished work and keeps the release gate blocked. Under your rule, it needs a fix unless you decide it’s too marginal and close it as won’t-fix.

Age alone is no reason to close them. The reason to close each is that its work is complete or you’ve explicitly decided against doing it.