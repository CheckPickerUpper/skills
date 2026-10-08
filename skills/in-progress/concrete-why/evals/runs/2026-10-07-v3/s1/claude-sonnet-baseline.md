There's less downside than I implied. I'd delete it.

**The one real cost is rollback speed.** Today, if checkout breaks, you flip `new_checkout_flow` off in LaunchDarkly and it's fixed in about a minute. That's how both incidents in the month before rollout were handled. After deletion, the same fix means reverting the PR and deploying, and your last 20 deploys took about 12 minutes from merge to live. So the worst case goes from about 1 minute to about 12 minutes of broken checkout, and only if something breaks.

**The risk of that happening looks low:**
- The flag has been at 100% since 2026-09-15, which is 22 days.
- There have been no checkout incidents in that time.
- LaunchDarkly shows no toggles since then, so nobody has needed the fallback.
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) says to remove it "once at 100% for 2 weeks with no incidents". That condition is met.

**Keeping it also has a cost, which I understated.** The legacy path is 412 lines across 6 files. Its 31 tests in `tests/checkout/legacy.spec.ts` add about 40s to every CI run. Those tests only cover code that no user can reach.

I said the legacy code "isn't hurting anything". The CI time is a small but real cost I should have counted.

The old code stays in git history, so a revert is still possible if you need it.

I'd remove the flag from `src/flags.ts`, delete `src/checkout/legacy/` and `tests/checkout/legacy.spec.ts`, and open a PR that closes #882. I'd also archive the flag in LaunchDarkly, but only after the deploy is live. If you want to keep the one-minute rollback a bit longer, the other option is to wait another week or two. Say the word and I'll start on the PR.
