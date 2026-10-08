Closing an issue in v3.2 does one concrete thing here: **it removes that issue from the release gate.** v3.2 can't ship while any issue in its milestone is open. If all four stay open, v3.2 stays blocked.

My earlier answer was wrong. "Stale" isn't a good reason to close any of them. One of them is a real bug, and closing it would just hide that bug while the release goes out. Here is each one:

| Issue | Actual state | What closing it does |
| --- | --- | --- |
| [#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) | Shipped in v2.3 by [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). That PR never linked the issue, so it stayed open. | Records it as done and unblocks v3.2. Leaving it open says the feature is missing when it isn't. |
| [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) | Fixed by [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470), which also didn't link it. | Same: records the fix and unblocks v3.2. |
| [#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) | v3.0 raised the minimum to Android 10 (`minSdkVersion 29`), so Android 9 users can't install current builds. The crash can't happen on anything we ship. | Closing it as "not planned" means officially dropping Android 9. That's a won't-fix, and won't-fix calls are yours to make. |
| [#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) | I reproduced it on `main` today: about a 150ms white flash on cold start with dark mode on. | Closing it would ship v3.2 with a known bug and lose the record of it. It shouldn't be closed. It should be fixed. |

My recommendation:

- **#402 and #404:** close as completed, each with a comment linking the PR that did the work.
- **#403:** close as not planned, because Android 9 is no longer supported. I'll only do this once you confirm dropping Android 9 is a deliberate decision.
- **#401:** fix it now, in its own PR with a regression test, before v3.2 ships. It's a low-priority bug, but it's been open 8 months, well past the 7-day deadline. Once that PR merges it closes #401 and v3.2 is unblocked.

The only thing I need from you is a yes or no on dropping Android 9 for #403. I can start the other three now.
