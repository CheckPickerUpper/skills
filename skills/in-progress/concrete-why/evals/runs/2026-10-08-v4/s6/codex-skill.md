Hora’s flurry checks whether the stamina-empty tag is present and moves to its final strike when it is. Checking `stamina === 0` could make the same decision; the concrete benefit of the tag is that Hora can use the ability runtime’s existing conditions without adding a condition for resource amounts.

**What Hora actually does**

[Hora.Ability.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:122) declares Hora’s phases for the shared ability runtime. Its flurry applies a stamina-draining effect and waits for any of three conditions:

```ts
// Hora.Ability.ts:132
Race: firstOf(
	onInputReleased(strikeNearestForward),
	// ▸ Releasing the button moves to the final strike.
	after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
	// ▸ Reaching the hold duration moves to the same strike.
	onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
	// ▸ Finding stamina's empty tag also moves to that strike.
),
```

There is no handwritten flurry loop here in which to insert an `if`. The phase describes its conditions, and the runtime checks them.

Importantly, **the tag condition itself checks current presence**. [PhaseGraphExecution.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAbilities/PhaseGraphExecution.ts:584), the shared runtime that executes Hora and other ability phases, does this:

```ts
// PhaseGraphExecution.ts:584
case "OnTagAdded": {
	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
	// ▸ Ask whether the participant has this tag right now.
	switch (presence.Kind) {
		case "Present":
			return { Kind: "WaitTriggered", Transition: wait.Transition };
			// ▸ Take the phase transition if it is present.
```

So the tag does **not** give Hora an immediate notification that a direct stamina check would lack.

**What the tag adds—and what your alternative costs**

[EmptyTag.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAttributes/EmptyTag.ts:71) contains `ResourceEmptyTags`, which the attribute container uses to update tags after resource changes:

```ts
// EmptyTag.ts:71
switch (limit.Kind) {
	case "AtZero":
	case "AtFloor":
		this.hold(marking.EmptyTag, at);
		// ▸ Put the resource's empty tag on at its lower limit.
		return;
	case "WithinLimits":
	case "AtCeiling":
		this.tags.RemoveEveryApplicationOf(marking.EmptyTag, at, BAR_ROSE);
		// ▸ Take the tag off when the resource is above its lower limit.
		return;
```

That is extra machinery compared with reading a number. Its gain is making “this resource is empty” available wherever gameplay already accepts tag conditions.

Your proposed check would conceptually be:

```ts
// Illustration, not the real code.
if (stamina === 0) {
	// ▸ Read the amount directly instead of its corresponding tag.
	moveToFinalStrike();
	// ▸ Produce the same phase change.
}
```

To express that inside Hora’s existing phase declaration, NRO would need an attribute-empty condition and runtime handling for it. The supported conditions in `GameplayWait`, the phase-condition type in [GameplayAbility.Types.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayDeclarations/GameplayAbility.Types.ts:629), include tags, input and timers, but no attribute-empty condition.

I found Hora as the only authored gameplay consumer of stamina’s empty tag. Other consumers are therefore a capability the tag enables, not demonstrated demand.

The decision document, [ADR 0038](/home/ozzy-desktop/dev/NRO-concrete-why-bench/docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md), says polling can go wrong between changes. I could not establish a timing advantage here: the current runtime checks tag presence too. A direct amount check at the same point would not inherently introduce that problem.

**My recommendation:** keep the tag with the current phase system, because Hora uses an existing condition in one line. But your comparison is right at the underlying level: reading zero requires less machinery than maintaining and reading a tag. What decides it is whether resource emptiness needs to work through NRO’s shared tag conditions, or only through this one ability’s amount check.