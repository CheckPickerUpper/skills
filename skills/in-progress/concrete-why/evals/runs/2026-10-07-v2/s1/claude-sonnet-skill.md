**Short answer:** There's no good reason to keep it. Delete it. My earlier "risky this soon" was a default, not an argument. Checked against the facts, the risk is small, and keeping the flag has a real cost.

**What deleting costs: the one-minute rollback goes away**
- Right now, if checkout breaks, someone flips `new_checkout_flow` off in LaunchDarkly and customers are back on the old path in about 1 minute. That is how both pre-rollout incidents ([the two in the month before 2026-09-15]) were mitigated.
- After deletion, the rollback is a revert and redeploy. A production deploy takes about 12 minutes from merge to live. So a checkout incident would last roughly 11 minutes longer than it would today.
- That is the whole downside. It is real, but it only matters if the new flow breaks.

**How likely that is**
- The flag has been at 100% since 2026-09-15 (about 3 weeks), with no toggles in the LaunchDarkly audit log and no checkout incidents.
- The old path (`src/checkout/legacy/`, 412 lines across 6 files) is only reachable when the flag is off. Nothing live uses it.
- Both earlier incidents came before rollout. I have no evidence of a problem since.

**What keeping it costs**
- `tests/checkout/legacy.spec.ts` (31 tests, legacy path only) adds about 40 seconds to every CI run, and tests code that no customer reaches.
- Anyone changing checkout has to work out which of two paths a change touches, and the 412 legacy lines stay in the codebase.
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) is open, and its own removal condition ("at 100% for 2 weeks with no incidents") has been met for about a week. Leaving it open means the repo's own criterion is being ignored.

**What decides it:** an 11-minute-longer outage in a scenario with no sign of happening, versus a permanent 40 seconds per CI run plus two code paths. After 3 quiet weeks, the second is the certain cost.

If you want a middle step, merge the deletion and keep the revert PR ready to go. That recovers most of the lost rollback speed (a revert still needs the 12-minute deploy). I'd just delete it, and the PR can close #882.
