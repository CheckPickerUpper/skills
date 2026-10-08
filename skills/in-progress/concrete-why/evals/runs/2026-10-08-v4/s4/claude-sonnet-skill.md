Closing doesn't change any code. It takes the issue out of v3.2's open count, and v3.2 is the release gate, so release is blocked while any issue in it is open. My earlier answers ("keeps the tracker clean", "no real benefit to leaving them open") were labels, not reasons, and "stale" didn't describe all four issues. The four come out differently, so I'm changing my recommendation: close two, leave one open, and leave one for you to decide.

**What closing does here**
1. All four issues sit in the v3.2 milestone.
2. Release is blocked while any issue in that milestone is open.
3. Closing an issue removes it from that count. If all four close, the gate has nothing left from them and v3.2 can ship.

So closing a bug that still exists unblocks a release that includes the bug.

**[#402 Export task list to CSV](https://github.com/CheckPickerUpper/tasklist-app/issues/402)** (a `feature` request)
It shipped in v2.3 in [#455 Add CSV export](https://github.com/CheckPickerUpper/tasklist-app/pull/455). That PR didn't reference #402, so GitHub never closed it automatically. Leaving it open blocks v3.2 for work that is already released. Close it, linking #455.

**[#404 Typo "recieve" in onboarding screen 2](https://github.com/CheckPickerUpper/tasklist-app/issues/404)** (a `bug`)
It was fixed in [#470 Onboarding copy fixes](https://github.com/CheckPickerUpper/tasklist-app/pull/470), which also didn't reference the issue. Same situation as #402: the work is done and only the closing is missing. Close it, linking #470.

**[#403 Crash on launch on Android 9](https://github.com/CheckPickerUpper/tasklist-app/issues/403)** (a `bug`)
v3.0 raised `minSdkVersion` to 29 (Android 10), so Android 9 users can't install current builds and can't hit the crash. Nothing is left to fix. Your rule says closing a bug as won't-fix is your decision, so this one is yours: I recommend closing it with a comment that points to the v3.0 change.

**[#401 Dark mode toggle flickers white on app load](https://github.com/CheckPickerUpper/tasklist-app/issues/401)** (a `bug`, priority low)
I reproduced this on `main` today. On a cold start with dark mode on, the screen shows a white flash for about 150ms. The last activity was 8 months ago, but the bug still happens. If I closed it:
1. The issue leaves v3.2's open count.
2. The gate clears.
3. v3.2 ships with the flash, and nothing in the tracker records it.

That also breaks your no-backlog rule: a bug should end fixed, or closed as won't-fix by you. Leave it open. Under your deadlines a low-priority bug is due within 7 days. I can't see its creation date, but I infer it's past due given the 8 months of inactivity. I'd fix it now, in its own PR with a regression test, before any feature work in this repo. If you'd rather give up on it, that is a won't-fix call for you to make.

**What I couldn't confirm:** I haven't checked whether other issues in v3.2 are open besides these four, so I don't know whether closing the right ones clears the gate.

**What decides it:** does the thing the issue describes still happen in the current build? #402, #404 and #403 don't, so closing them records what's already true. #401 does, so closing it would hide a live bug.
