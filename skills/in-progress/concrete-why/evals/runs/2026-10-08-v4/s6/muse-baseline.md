In NRO, `Stamina == 0` inside Hora's flurry is the special case — the tag is the general mechanism.

Hora's flurry is a phase-graph race:

[Hora.Ability.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:132) — `firstOf(onInputReleased, after(maxHold), onTagAdded(Stamina.WhileEmpty.EmptyTag))`.

Why that, per [ADR 0038](docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md):

1. **Everything already speaks tags.** `onTagAdded` races, activation gates, `runsWhileTagged` effect conditions, and gameplay cues all read tags. Making "empty" a tag makes it visible to all of them at once. A `stamina == 0` check inside Hora helps only Hora; gates/cues/conditions would each need their own copy.
2. **One owner, no disagreement.** The attribute container already changes the number, so it sets/clears the `EmptyTag` in the [same change](src/Shared/ReplicatedStorage/GameplayAttributes/GameplayAttributeContainer.ts:656) that moves the number. "Empty" also isn't always `0` — e.g. Health's lower limit is `1` — so the container knowing the limit beats every reader hardcoding zero.
3. **Prediction comes free.** The container is shared code, so client and server derive "empty" from the same change.

The ADR explicitly rejects your two simpler alternatives: an `onAttributeEmpty(Stamina)` race (ability runtime would need a second watch mechanism, and gates/cues still couldn't see it), and polling the bar every tick (infers state from a side effect, and goes wrong when the check lands between changes).
