**Short answer:** Delete it. The only concrete downside is that a checkout bug would take about 13 minutes to undo instead of 1. My earlier "safety net" and "risky this soon" were labels, not reasons, and the facts below don't support them.

**What deleting gives up**

The flag `new_checkout_flow` (in `src/flags.ts`, served by LaunchDarkly) is the only way back to the old checkout. It has been at 100% of traffic since 2026-09-15, and the old path in `src/checkout/legacy/` (412 lines across 6 files) only runs when the flag is off. Here is what happens if the new flow breaks after the delete:

1. A checkout bug reaches customers.
2. Today, someone flips the flag off in LaunchDarkly. Both incidents from the month before rollout were fixed this way, in about 1 minute each.
3. After the delete, there is no flag to flip. Someone has to revert the deletion and merge it, then wait for the deploy. The last 20 production deploys of storefront took about 12 minutes from merge to live.
4. So checkout stays broken for roughly 13 minutes instead of 1. That is about 12 extra minutes during which customers can hit the bug.

The incident log shows no checkout incidents since 2026-09-15. The two incidents before that date are the only evidence that the flag has ever been needed.

**What keeping it costs**

- `tests/checkout/legacy.spec.ts` has 31 tests that only exercise the legacy path. They add about 40 seconds to every CI run.
- The 412 legacy lines stay in the repo, reachable only if someone turns the flag off.
- [#882 Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) is open. Its body says "remove once at 100% for 2 weeks with no incidents." The flag has been at 100% for about 3 weeks, and LaunchDarkly's audit log shows no toggles since then. The issue's condition is met, and its remove-after-two-weeks rule is the plan we already wrote down.

**What I couldn't confirm**

- Whether the 3 weeks included a traffic peak, such as a sale or a payday weekend. I only know there were no incidents. If a big peak is coming in the next few weeks, that is a reason to wait for it, and the 13-minute figure matters more then.
- Whether anything besides `src/checkout/` reads `new_checkout_flow`. Check before deleting.
- Whether a revert would merge cleanly. The 13 minutes assumes it does.

**What decides it:** the flag buys 12 minutes of faster recovery from a bug that has not appeared in 3 weeks. Against that, every CI run pays 40 seconds and #882's own condition has been met. If a known high-traffic event is coming soon, wait until it passes. Otherwise, delete it.
