Hora checks an “empty stamina” tag because its flurry is declared as three competing ways to finish: release the button, reach the time limit, or run out of stamina. **A direct stamina check could produce the same behavior; the concrete benefit of the tag is reusing the ability runtime’s existing condition check.**

The flurry declaration in [Hora.Ability.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:122), which the ability runtime executes, contains this:

```ts
// Hora.Ability.ts:132
Race: firstOf(
	onInputReleased(strikeNearestForward),
	// ▸ Releasing the button moves to the final strike.
	after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
	// ▸ Holding for the full duration moves to the same strike.
	onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
	// ▸ Empty stamina moves to that strike too.
),
```

Hora doesn’t calculate whether stamina is empty here. The shared attribute code that changes resource amounts maintains that fact for it. In [EmptyTag.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAttributes/EmptyTag.ts:71), `ResourceEmptyTags` adds or removes each resource’s declared tag:

```ts
// EmptyTag.ts:71
switch (limit.Kind) {
	case "AtZero":
	case "AtFloor":
		this.hold(marking.EmptyTag, at);
		// ▸ Put the empty tag on when the resource reaches its lower limit.
		return;
	case "WithinLimits":
	case "AtCeiling":
		this.tags.RemoveEveryApplicationOf(marking.EmptyTag, at, BAR_ROSE);
		// ▸ Take it off when the resource rises above that limit.
		return;
	// ...
}
```

That **is additional machinery**: the resource number is stored, and its empty/not-empty condition is also represented in the tag container.

Your proposed check would avoid that representation. Conceptually:

```ts
// Proposed alternative, not existing repository code:
if (attributes.ReadGameplayAttribute(Resources.Stamina) === 0) {
	// ▸ Read the resource number directly.
	// Transition to Hora's final strike.
}
```

The comparison itself is simpler. But Hora’s declaration needs a condition the runtime can evaluate alongside button release and timeout. You would either add an attribute condition to that runtime or give Hora a separate execution path for this check.

There’s also an important qualification: **the tag does not eliminate polling.** In [PhaseGraphExecution.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAbilities/PhaseGraphExecution.ts:584), the runtime that advances ability phases implements `onTagAdded` by checking current tag presence:

```ts
// PhaseGraphExecution.ts:584
case "OnTagAdded": {
	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
	// ▸ Ask whether the tag is present now.
	switch (presence.Kind) {
		case "Present":
			return { Kind: "WaitTriggered", Transition: wait.Transition };
			// ▸ Advance to the declared destination.
		case "Absent":
			return AwaitingEventPending;
			// ▸ Keep waiting.
		// ...
	}
}
```

So I would not defend this with “checking stamina each tick is unreliable, but tags catch the exact instant.” This implementation checks a tag instead of a number.

[ADR 0038](/home/ozzy-desktop/dev/NRO/docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md:1), the repository’s accepted design decision for empty resource bars, also intends tags to make emptiness available to activation gates, effect conditions, and cues. **I found Hora as the only gameplay consumer explicitly referencing the stamina-empty tag.** Those other uses are an architectural benefit the design enables, rather than additional stamina consumers I verified. I did not run builds or tests.

For Hora alone, you’re right that a direct check needs less machinery. In NRO’s current ability system, the tag lets Hora express that check through a condition the runtime already understands. What decides it is whether resource emptiness belongs in that shared condition system or only in this attack’s execution.