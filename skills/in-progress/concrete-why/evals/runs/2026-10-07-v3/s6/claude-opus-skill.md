Hora has no code body where an `if (stamina === 0)` could go. It is a list of declarations, and the flurry can only end on one of the race triggers the phase runtime already supports. "Stamina ran out" was made a tag so Hora could use the existing `onTagAdded` trigger. The alternative is a new trigger kind in the runtime. One of the reasons on record for the tag, that it times better than reading the number, doesn't hold up against the code (more on that below). The case for the tag rests on reuse, and on Health's floor being 1 rather than 0. I'd keep it, but not for the timing reason.

**What Hora's flurry is**

`Hora.Ability.ts` is the content file for the Silver Rapier hold attack. It declares four phases (windup, flurry, strike, recovery) as data. The phase runtime, `PhaseGraphExecution.ts`, runs them on both the server and the client. The flurry ends on whichever of three triggers fires first:

```ts
// Hora.Ability.ts:131
Continuation: {
	Kind: "Await",
	Race: firstOf(
	// ▸ "First of": whichever trigger fires first decides what happens next.
		onInputReleased(strikeNearestForward),
		// ▸ The player let go of the button.
		after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
		// ▸ 1.5 seconds have passed.
		onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
		// ▸ The "Stamina empty" tag appeared on the player.
	),
},
```

The runtime only accepts a fixed set of trigger kinds, listed in `PhaseGraph.ts:184–302`: `After`, `OnInputReleased`, `OnInputPressed`, `OnOwnerDied`, `OnTagAdded`, `OnTagRemoved`, `OnIncomingAttack`, `OnAttackFinished` and `OnTargetLost`. None of them reads an attribute. So "check if stamina is 0 inside the flurry" really means adding a tenth kind, something like `onAttributeEmpty(Stamina)`. ADR 0038 (`docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`, the decision record for this) lists that exact option and rejects it.

**What that check would cost**

`PhaseGraphExecution.ts` has four exhaustive switches over trigger kinds:
- `pressTransition` (line 56)
- `readWaitPaces` (line 479)
- `recordObservedTagIfPresent` (line 513)
- `checkWaitTriggered` (line 542)

A new kind needs an arm in each of them. It also needs a new type next to `OnTagAdded` in `GameplayAbility.Types.ts:607`, a factory function in `PhaseGraph.ts`, and the code that actually reads the attribute. With the tag, Hora needed one line and no runtime changes.

**What the tag costs, and what it does**

The tag is a 7-line declaration:

```ts
// State.GameplayTag.ts:212
export const StateResourceEmptyStamina = createBinaryTag({
	Placement: under(StateResourceEmpty),
	// ▸ Sits under the Empty tag family, next to Health, Chakra, BlockBar and Awakening.
	Segment: tagSegment("Stamina"),
	Name: "Stamina empty",
	Description: "Stamina is at its lower limit.",
	Gate: alwaysApplies(),
	Exclusion: sitsFreely(),
});
```

Nothing calls it from gameplay code. The attribute container, which holds every number on a player, keeps the tag in step with the bar on every change:

```ts
// GameplayAttributeContainer.ts:649
private recordChange(change: GameplayAttributeChange): void {
	this.versions.RecordChange(change.Attribute);
	writeAttributeChange(this.log, change);
	this.settleEmptyTag(change.Attribute, change.OccurredAt);
	// ▸ Every write, cost and modifier change passes through here.
	// ▸ It puts the empty tag on or takes it off to match the new reading.
}
```

```ts
// EmptyTag.ts:71, inside ResourceEmptyTags.Settle
switch (limit.Kind) {
	case "AtZero":
	case "AtFloor":
	// ▸ The bar is at its lower limit, whatever that limit is.
		this.hold(marking.EmptyTag, at);
		return;
	case "WithinLimits":
	case "AtCeiling":
		this.tags.RemoveEveryApplicationOf(marking.EmptyTag, at, BAR_ROSE);
		// ▸ The bar rose, so the tag comes off in the same step.
		return;
```

`ResourceEmptyTags` (`src/Shared/ReplicatedStorage/GameplayAttributes/EmptyTag.ts`, about 115 lines) is shared by all five bars. It was not written for Hora alone.

**"Empty" is not always "0"**

The tag means "at its lower limit". Stamina's limit is zero (`Resources.GameplayAttribute.ts:109`, `ordinaryZeroFloor`), so for Hora the tag and `stamina === 0` match exactly. Health's limit is not zero:

```ts
// Resources.GameplayAttribute.ts:98
LowerLimit: floorAt(attributeAmount(1)),
// ▸ Health stops at 1 and a knockdown takes over from there.
```

Copy the `=== 0` pattern to a future "ends when Health runs out" ability and it never fires, because Health never reaches 0. The tag is already defined against each bar's own floor.

**Where my earlier reasoning, and the ADR's, is empty**

- ADR 0038 says polling the bar "goes wrong whenever the check runs between changes." The runtime does the same kind of polling for the tag. On each step it reads whether the tag is present right now:

  ```ts
  // PhaseGraphExecution.ts:584
  case "OnTagAdded": {
  	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
  	// ▸ A read of the current state, made at the same moment a stamina read would be.
  	switch (presence.Kind) {
  		case "Present":
  			return { Kind: "WaitTriggered", Transition: wait.Transition };
  ```

  The tag also comes off the moment the bar rises. So if stamina hit 0 and regenerated before the check, both approaches would miss it the same way. The timing argument is not a reason.
- The ADR also says "it infers state from a side effect, which the repo forbids." Reading Stamina isn't inferring from a side effect, though. Stamina is the fact itself. I don't count this one either.
- "Prediction works the same way" doesn't matter for Hora. Hora is declared `Prediction: WaitsForServer`, so the client doesn't guess its flurry ending.
- "Gates, cues and effect conditions can all read it": today nothing else does. The only readers of `StateResourceEmptyStamina` are Hora and one test, `AttributeComposition.integration.ts`. That benefit is possible later, not current.

**What I couldn't confirm:** I didn't trace how a new attribute trigger would read Stamina through `host.Owner`. `ReadWaitPace` reads attributes through formulas, so some way in exists, but I haven't sized that part.

**What decides it:** does the runtime already have a trigger for the fact? For "stamina ran out" it does (`onTagAdded`), and the tag knows each bar's real floor. A direct stamina check would be a second trigger kind that only works for bars whose floor is 0.
