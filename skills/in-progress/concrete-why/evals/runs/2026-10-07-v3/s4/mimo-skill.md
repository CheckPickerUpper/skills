Closing removes an issue from the open set, which is the only thing the v3.2 release gate looks at; leaving it open keeps v3.2 blocked on it. My earlier answers ("clean", "noise", "reflects reality") were labels, not reasons — here is what each option actually does, per issue, and one of my four closures I'm taking back.

**What closing does mechanically**

`CheckPickerUpper/tasklist-app` uses milestone "v3.2" as the release gate: release is blocked while any issue in it is open. Closing an issue is what takes it out of that open set. The thread stays readable, stays linked from any PR, and can be reopened with one click. Leaving it open is not a neutral state here — it's a standing "release cannot go out" flag.

**What leaving #402 and #404 open does**

[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402) (label `feature`, in v3.2) is work that already shipped: [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455) landed the CSV export in v2.3. #455 didn't write "#402" anywhere, which is the only reason #402 is still open. [#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404) (label `bug`, in v3.2) is the same shape: [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470) fixed the typo; #470 didn't reference #404.

Leaving these open produces one specific sequence:
1. Someone decides v3.2 is ready and checks the gate.
2. The gate reads four open issues in v3.2.
3. Two of them describe work that shipped in v2.3 and in #470.
4. The release waits on work that is already in users' hands.

Closing them with a comment naming #455 and #470 makes the tracker match the app and unblocks the gate. Nothing is lost: the PRs are one click away in the closure comment.

**What leaving #403 open does**

[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403) (label `bug`, in v3.2) describes a crash on a platform current builds cannot reach: v3.0 raised `minSdkVersion` to 29, so Android 9 users cannot install v3.x at all. Leaving it open blocks v3.2 on a bug that no user of a v3.2 build can hit. Closing it as won't-fix / not-applicable is a record that "we dropped Android 9 instead of fixing this" — which is a decision, and per your standing rule that call is yours, not mine.

**What leaving #401 open does — and why I'm reversing my earlier recommendation**

[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401) (label `bug`, priority low, in v3.2) is not stale in the sense that matters. I reproduced it on `main` today: with dark mode on, a cold start shows roughly 150ms of white before the dark theme paints. The sequence is:

1. The app process starts with dark mode selected in settings.
2. The window paints before the theme is applied to the first frame.
3. The user sees a white flash for ~150ms, then the dark UI.

Closing it as stale would record "this no longer happens" in a tracker whose gate you rely on, while it happens on every cold start today. Your standing rule gives exactly two endings for a bug: fixed, or closed as won't-fix by your decision. #401 is neither yet — so my earlier "close all four as stale" was wrong for this one. It gets fixed, or you decide the flash is acceptable and I close it as won't-fix with that reasoning in the comment.

**What I couldn't confirm:** whether the v3.2 gate is enforced by automation that reads milestone state or by a human checking it before release — the blocking behavior is real either way, but I didn't verify the mechanism. I also don't know why #455 and #470 omitted their issue numbers; I only verified that they did.

**What decides it:** can the problem the issue describes still happen on a build a user can install today? #401 can, so it stays open or gets fixed; #402 and #404 already shipped, so open is a false statement about the app; #403 can't happen on installable builds, so it closes as your won't-fix call.
