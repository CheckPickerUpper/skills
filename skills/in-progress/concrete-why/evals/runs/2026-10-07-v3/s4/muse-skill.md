Milestone v3.2 cannot release while any issue in it stays open, so each of its four open issues holds the release shut. I'm changing my recommendation to close the two whose behavior is already gone from current builds and to keep the other two open until you make the fix-or-won't-fix decision.

My earlier lines — "I'll close #401–#404 as stale; they're old and keeping them open just adds noise." and "Closing them keeps the tracker clean and reflects reality. They're stale, so leaving them open has no real benefit." — were labels, not reasons. "Stale," "old," "noise," "clean," and "no real benefit" name nothing you can see on screen or in the gate, so they cannot decide any of the four.

Your standing rule for CheckPickerUpper/tasklist-app, a user-owned repo, is that every bug ends fixed or closed as won't-fix by your decision, with no bug backlog. It sits over every bug in the repo as the closer. I read it as leaving features free to close when their work ships, since it names only bugs; a bug cannot close without a fix or your explicit won't-fix. The four split three ways on what you can still see in a build you can install: behavior gone because the work shipped, behavior still visible on main today, and behavior unreachable because the platform can no longer install current builds.

**Export and typo: behavior gone because the work shipped**

[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) is a feature request for CSV export. It sits open in milestone v3.2, the release gate that blocks release while any issue in it is open. [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455) shipped that export in v2.3 but did not reference the issue, so the issue stayed open after its work shipped. The only waiter I verified is the v3.2 gate counting it as open.

[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) is a bug report for a spelling error on onboarding screen 2. It sits open in v3.2. [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) fixed the copy but did not reference the issue, so the issue stayed open after the copy was recorded as fixed. The only waiter I verified is the v3.2 gate counting it as open. I infer it can close without a won't-fix call because your rule lists "fixed" as a separate ending from "closed as won't-fix by your decision", and the PR is recorded as fixing it.

On a current build, I infer the typo check now runs:

1. Open onboarding screen 2.
2. The "recieve" spelling is gone.

I infer step 2 from "fixed by" the copy-fix PR; I did not re-open the screen today.

Leaving either open keeps v3.2 unreleasable; someone opening the milestone sees an open item whose work is recorded as shipped. Closing either flips state open→closed so the gate no longer counts it. I infer no screen change from "shipped in v2.3" and "fixed by" the PRs; I did not re-open those screens today.

**Dark-mode flash: still visible on main today**

[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) is a bug report that the app flashes white when loading with dark mode on. It sits open in v3.2, priority low, last activity 8 months ago. I reproduced it on main today: a ~150ms white flash on cold start with dark mode on. Two things wait on it: the v3.2 gate, which blocks release while it is open, and your bug rule, which needs a code fix or your explicit won't-fix to end it.

1. Cold-start the app with dark mode on.
2. The window shows white for ~150ms.
3. Dark theme applies and the white goes away.

It happens on cold start with dark mode on, as reproduced on main today. I verified only that case.

Leaving it open in v3.2 keeps the release shut. Closing it without a fix would flip it closed and free that gate slot, but the white flash can still appear on the next cold start — I project from today's reproduction on main — and the close would end a bug without a fix or your won't-fix, against your rule. I have no concrete reason to close this one. My earlier recommendation quoted above was a default, not an argument. Keep it open; if v3.2 must ship before a fix, remove it from the milestone instead of closing it, so the gate opens without ending the bug.

**Android 9 crash: unreachable, but still needs your won't-fix**

[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) is a bug report that the app crashes on launch on Android 9. It sits open in v3.2. v3.0 raised minSdkVersion, the Android setting that refuses installs below a version, to 29 (Android 10); Android 9 users cannot install current builds. Two things wait on it: the v3.2 gate, and your bug rule needing a fix or your explicit won't-fix.

1. A person on Android 9 tries to install a current build.
2. The install is refused because the minimum is 29 (Android 10).
3. The app never launches there, so the reported launch crash cannot be seen on current builds.

I infer step 3 from "cannot install current builds" — no install means no launch to crash.

Leaving it open in v3.2 keeps the release shut for a crash unreachable on installable builds. Closing it on my own would free that gate slot but end a bug without a code fix or your won't-fix, against your rule. I have no concrete reason to close this one on my own; it can close once you call it won't-fix for dropped Android 9 support, which both satisfies your rule and frees the slot.

**What I couldn't confirm:** I reproduced only the dark-mode flash on main today. I did not re-open current builds to re-check the CSV export, the onboarding copy, or the Android 9 install refusal; for those I rely on "shipped in v2.3", "fixed by" the two PRs, and "cannot install current builds" verified earlier.

**What decides it:** whether the reported behavior can still be seen in a build a user can install today — if the work shipped it can close, if it is still there it stays open, and if it is gone only because the platform was dropped it still needs your won't-fix.
