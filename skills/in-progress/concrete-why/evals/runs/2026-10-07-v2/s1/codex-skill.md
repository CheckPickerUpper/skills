We can delete it now: it meets the agreed removal condition. My earlier “risky this soon” wasn’t a reason, and “the legacy code isn’t hurting anything” was wrong—it adds about 40 seconds to every CI run.

The concrete downside is losing the fast fallback. `new_checkout_flow`, the LaunchDarkly switch in `src/flags.ts`, lets us return to the old checkout:

- **If we delete it and the legacy path:** a checkout incident can no longer be mitigated by switching the flag off. That worked in about one minute for both incidents before rollout. A mitigation requiring a code change would take preparation time plus about 12 minutes from merge to live.
- **If we keep it:** that fallback remains available, but we retain 412 lines across six legacy files and 31 legacy-only tests that add about 40 seconds to every CI run.

[Remove legacy checkout after new flow is stable](https://github.com/acme/storefront/issues/882) sets the removal condition: two weeks at 100% traffic with no incidents. We’ve had about three weeks, with no checkout incidents or flag toggles.

What decides it is whether to retain the one-minute fallback beyond that agreed window. There is a concrete cost to deleting it, but the condition we set for accepting that cost has been met.