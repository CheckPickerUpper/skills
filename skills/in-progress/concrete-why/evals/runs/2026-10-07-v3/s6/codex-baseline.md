**For Hora alone, checking `stamina === 0` would be simpler.** NRO uses a tag because it treats “stamina is empty” as a shared gameplay condition that abilities, activation requirements, effects, and cues can all read through the same mechanism. That decision is recorded in [ADR 0038](/home/ozzy-desktop/dev/NRO/docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md).

The resource code maintains the tag when stamina changes and removes it when stamina rises. [Hora’s flurry](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:130) then waits for release, timeout, or that tag to perform its final strike. Hora doesn’t separately maintain “out of stamina.”

There’s a fair qualification, though: **the tag doesn’t make a zero check inherently more correct.** The current ability runtime checks whether the tag is present when evaluating its waits; it isn’t an immediate callback from the stamina change. A direct stamina condition evaluated there could also work.

So the reason is reuse across NRO’s gameplay systems. Your suggestion is simpler locally; the tag keeps the existing general mechanism consistent.