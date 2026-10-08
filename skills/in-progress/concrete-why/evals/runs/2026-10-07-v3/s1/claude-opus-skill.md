**Short answer:** The one real downside is rollback speed. Today a bad checkout gets switched back to the old path in about a minute. After deletion, it takes a code revert plus a deploy of about 12 minutes. Issue #882 set its own bar for removal, and we've cleared it. I'm changing my recommendation: delete the flag.

**My earlier answer**

I said "it's a safety net, removing it is risky this soon, the legacy code isn't hurting anything." "Risky" and "safety net" were labels, not reasons. "Isn't hurting anything" was wrong, because the legacy code costs CI time (details below).

**What you lose by deleting: the one-minute rollback**

`new_checkout_flow` is defined in `src/flags.ts` and controlled from LaunchDarkly, our feature-flag service. It decides which checkout code runs:

- **Flag on:** the new checkout runs. It has been on for 100% of traffic since 2026-09-15, about 3 weeks. The LaunchDarkly audit log shows no toggles since then.
- **Flag off:** the old checkout runs. That's `src/checkout/legacy/`, 412 lines across 6 files, and nothing else can reach it.

Here's what a checkout problem looks like with the flag:

1. Something breaks in the new checkout.
2. Someone switches the flag off in LaunchDarkly.
3. Customers are back on the legacy path in about a minute.

That's exactly how the two incidents in the month before rollout were fixed: one flag switch each, about 1 minute to mitigate.

After deletion, the same problem goes like this:

1. Something breaks in the new checkout.
2. Someone opens a revert of the removal PR and gets it merged.
3. The deploy runs. Over the last 20 deploys, that's about 12 minutes from merge to live.

So the cost is roughly 12 minutes plus however long step 2 takes, compared with about 1 minute. It only matters if the new flow breaks in a way the old flow wouldn't. That hasn't happened in the 3 weeks at full traffic: there have been no checkout incidents since 2026-09-15.

**What keeping the flag costs**

- `tests/checkout/legacy.spec.ts` has 31 tests, and all of them exercise only the legacy path. They add about 40 seconds to every CI run, on code no customer has reached in 3 weeks.
- There are 412 lines of checkout code that still need reading and maintaining but never run in production.

**What #882 already decided**

[#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) is the open issue for this cleanup. Its body sets the condition: "remove once at 100% for 2 weeks with no incidents." We're at 3 weeks with no incidents.

**What I couldn't confirm:** I only checked `src/flags.ts` and the storefront code paths. I haven't verified that nothing outside storefront reads `new_checkout_flow` from LaunchDarkly, such as another service or an analytics dashboard. Before archiving the flag in LaunchDarkly, I'll check its usage/insights page there.

**What decides it:** whether being able to roll back in about a minute instead of about 12 is still worth something. Three weeks at full traffic with no incidents, plus the condition #882 set itself, say it isn't.

I'll do this as one PR that closes #882. It will remove `src/checkout/legacy/`, `tests/checkout/legacy.spec.ts` and the flag check, and leave archiving the flag in LaunchDarkly until after the deploy is live.
