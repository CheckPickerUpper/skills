You can delete it. The one real downside is slower rollback: today a broken new checkout can be switched off in about a minute, and after deletion it takes a revert and a deploy of about 12 minutes or more. Three weeks at 100% with no incidents meets the bar the cleanup issue set, so I'm changing my recommendation: remove it.

**My earlier answer wasn't a real argument.** I wrote: "It's a safety net and removing it is risky this soon; the legacy code isn't hurting anything." "Safety net" and "risky" were labels without a consequence attached. "Isn't hurting anything" was wrong, because the legacy code adds about 40 seconds to every CI run (details below).

**The downside: rollback goes from a flag flip to a deploy**

`new_checkout_flow` is the flag in `src/flags.ts`, served by LaunchDarkly. It picks between the new checkout and the old one in `src/checkout/legacy/`. It has been at 100% since 2026-09-15, and the LaunchDarkly audit log shows no toggles since then.

Here is what happens if the new checkout breaks today:
1. Someone turns `new_checkout_flow` off in LaunchDarkly.
2. Traffic goes back to `src/checkout/legacy/`. In the two incidents in the month before rollout, this took about 1 minute each.

And after the flag is deleted:
1. Someone writes a fix or a revert PR and merges it.
2. The deploy runs. Over the last 20 deploys, merge to live took about 12 minutes.
3. Checkout stays broken until that deploy lands, which is 12 minutes plus however long step 1 takes.

That gap only matters if the new checkout has an incident. There have been none since 2026-09-15.

**What keeping it costs**

- `src/checkout/legacy/` is 412 lines across 6 files. Nothing reaches it while the flag is on, and the flag has been on for every user for 3 weeks.
- `tests/checkout/legacy.spec.ts` has 31 tests that only exercise that legacy path. They add about 40 seconds to every CI run.

**The issue already set the condition**

[#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) is open. Its body says "remove once at 100% for 2 weeks with no incidents." It has been about 3 weeks with no incidents.

**What I couldn't confirm:** I didn't check whether the legacy path still works with today's code and backend. The 1-minute rollback only exists if switching back lands on a checkout that works. Nobody has been served the legacy path since 2026-09-15, so the safety net may be weaker than I assumed.

**What decides it:** is a possible 11-minute-longer outage on a checkout incident worth 40 seconds on every CI run and 412 dead lines? After 3 weeks clean, and with #882's own bar met, it isn't. Removing the flag, `src/checkout/legacy/` and `tests/checkout/legacy.spec.ts` in one PR that closes #882 is the cleanup.
