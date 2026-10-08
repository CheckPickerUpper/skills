**For Hora alone, checking `stamina === 0` would be simpler.** NRO uses a tag so the same condition works throughout its existing gameplay system.

[Hora’s flurry](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:135) declares three ways to reach its final strike: release the button, reach the hold limit, or have stamina’s empty tag present. The attribute container maintains that tag when stamina changes and removes it when stamina rises.

That makes “stamina is empty” available to ability phases, activation gates, effect conditions, and cues through their existing tag support. A direct numeric check would need support in the phase system; other consumers would need their own equivalent support. That’s the rationale recorded in [ADR 0038](/home/ozzy-desktop/dev/NRO-concrete-why-bench/docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md).

**Your objection is valid about the check itself:** comparing a number to zero is perfectly sound. The tag buys reuse, not a better comparison. Despite the name `onTagAdded`, the runtime actually checks tag presence when evaluating the wait—so this isn’t inherently more event-driven than checking stamina.

I’d keep it given NRO’s shared tag-based rules, but justify it by that reuse, not by claiming a zero check is wrong.