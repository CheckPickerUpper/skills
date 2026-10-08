The container puts Stamina's empty tag on in the same step its writes move the number to 0, and Hora's flurry waits on that tag with the same wait kind it already uses for release and timeout. Keep the tag: a `== 0` check inside the flurry reads the same answer for Stamina today, but it copies the floor into the ability and needs a wait kind the phase runtime doesn't have.

**How the flurry ends today**

[Hora.Ability.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts) is the rapier ability declaration: windup pays 20 Stamina, the flurry drains 20 a second while held, and the strike hits whoever is nearest in front. Its flurry phase races three waits; the third is the tag:

```ts
// Hora.Ability.ts:130, inside the flurry phase definition
Continuation: {
	Kind: "Await",
	Race: firstOf(
		onInputReleased(strikeNearestForward),
		// ▸ The player let go: strike now.
		after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
		// ▸ Held the full 1.5 seconds: strike now.
		onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
		// ▸ Stamina's Empty Tag appeared: strike now.
	),
},
```

`Resources.Stamina` ([Resources.GameplayAttribute.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/Content/GameplayAttributes/Resources.GameplayAttribute.ts:106)) is the kept number for current stamina. It declares its Empty Tag on the same lines as its floor, and the tag itself ([State.GameplayTag.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/Content/GameplayTags/State.GameplayTag.ts:212)) is one binary tag under `State/Resource/Empty`. Only Hora's flurry reads the Stamina one today; the other matches for it are the declaration, the generated content catalog, and tests.

The tag is settled by `ResourceEmptyTags` ([EmptyTag.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAttributes/EmptyTag.ts:48)), which holds one participant's tags, called from one place: `recordChange` ([GameplayAttributeContainer.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAttributes/GameplayAttributeContainer.ts:649)), which every public write path reaches (write, increase, refill, reduce, change, cost pay, modifier on, modifier off):

```ts
// GameplayAttributeContainer.ts:642
/**
 * Lands one change in the same step the number moved: marks it unseen for every reader, writes it to the
 * log, and puts the number's Empty Tag on or takes it off to match what the number now reads.
 *
 * Every write, cost, and modifier going on or coming off reaches here, so a bar's Empty Tag can never
 * disagree with the bar, and nothing has to watch the number to find out it ran dry.
 */
private recordChange(change: GameplayAttributeChange): void {
	this.versions.RecordChange(change.Attribute);
	writeAttributeChange(this.log, change);
	this.settleEmptyTag(change.Attribute, change.OccurredAt);
	// ▸ The tag moves in the same step as the number, on every route that moves the number.
}
```

`Settle` puts the tag on when the reading rests on its lower limit and takes it off otherwise:

```ts
// EmptyTag.ts:60
public Settle(attribute: AttributeDefinition, limit: HoldingLimit, at: number): void {
	const marking = emptyMarkingFor(attribute);
	// ▸ Which tag this number declares, if it is a bar at all.
	// ...
	switch (limit.Kind) {
		case "AtZero":
		case "AtFloor":
			this.hold(marking.EmptyTag, at);
			// ▸ Bar is on its lower limit: tag goes on (once; a second empty change adds nothing).
			return;
		case "WithinLimits":
		case "AtCeiling":
			this.tags.RemoveEveryApplicationOf(marking.EmptyTag, at, BAR_ROSE);
			// ▸ Bar rose: tag comes off in the same step.
			return;
		// ...
	}
}
```

Starting bars are settled before gameplay gets the container ([composeGameplayAttributes.Shared.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAttributes/Composition/composeGameplayAttributes.Shared.ts:34)), and [AttributeComposition.integration.ts](/home/ozzy-desktop/dev/NRO/src/_Testing_/_Tests_/AttributeComposition.integration.ts:44) proves it: empty health carries its tag immediately, positive stamina never does.

**What `stamina == 0` inside the flurry would need**

`PhaseGraphExecution` ([PhaseGraphExecution.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAbilities/PhaseGraphExecution.ts:542)) is the step runner that checks each open wait. It reaches the fighter only through `ActivationOwner` ([PhaseGraphExecutionHost.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAbilities/PhaseGraphExecutionHost.ts:139)):

```ts
// PhaseGraphExecutionHost.ts:139
/** Facts about the fighter running the ability: tags it carries and how fast its paced waits run. */
export interface ActivationOwner {
	readonly ReadTagPresence: (queryTag: GameplayTagDefinition) => GameplayAbilityTagPresence;
	// ▸ The only gameplay fact a wait can ask about: is this tag on?
	readonly ReadWaitPace: (wait: AfterWait) => number;
	// ▸ How fast a timed wait runs. Not a number reading.
}
```

The `OnTagAdded` check reads through that one method:

```ts
// PhaseGraphExecution.ts:584
case "OnTagAdded": {
	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
	// ▸ Ask the fighter's tags, not its numbers.
	switch (presence.Kind) {
		case "Present":
			return { Kind: "WaitTriggered", Transition: wait.Transition };
		case "Absent":
			return AwaitingEventPending;
	// ...
```

The four exhaustive switches in that file enumerate nine wait kinds (`After`, `OnInputReleased`, `OnInputPressed`, `OnOwnerDied`, `OnTagAdded`, `OnTagRemoved`, `OnIncomingAttack`, `OnAttackFinished`, `OnTargetLost`); none reads a number. I infer a stamina check would need a tenth wait kind, a new host method beside `ReadTagPresence`, and a branch in each of the four switches, which all end in `unreachable(wait)`. The same wait is already reused elsewhere with no new machinery: the M1 string cancels on `onTagAdded(StatusStunned, ...)` and `onTagAdded(StateCombatAbilityLocked, ...)` ([M1String.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayDeclarations/M1String.ts:355)).

**"Way simpler"**: the tag side is one declared line per bar (`EmptyTag: StateResourceEmptyStamina`), required by the parameter type of `createAddressedResourceAttribute`, so a sixth bar that forgets it fails to compile ([AddressedGameplayAttribute.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAttributes/AddressedGameplayAttribute.ts:170)). The check side is one comparison plus a new wait kind, a new host method, four new switch branches, and then a copy in every other surface that asks about empty: gates take tag queries (`onlyIf(CanUseAbilities)` on Hora itself), effect conditions take `runsWhileTagged`, and the sequence runtime already shows what a second mechanism looks like — it carries its own resource-aware wait, `UntilInputReleasedOrResourceFull`. Tag-gated rules are re-read the moment tags move; anything else is settled when read and does not follow the fight until read again ([GameplayCondition.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayDeclarations/GameplayCondition.ts:399)):

```ts
// GameplayCondition.ts:399
/**
 * Writes down the gameplay tags that have to stay on somebody for a rule to keep acting on them.
 *
 * Watched rather than asked for every frame: the tags somebody carries report the moment one moves, so a
 * rule written this way is re-read then and at no other time.
 */
export function runsWhileTagged(Tags: GameplayTagQuery): NumberModifierGate {
	return { Kind: "OnlyIf", Tags };
	// ▸ A gate on "stamina empty" follows the fight by itself once empty is a tag.
}
/**
 * Writes down what has to stay true of the fight for a rule to keep acting on somebody.
 *
 * For facts a set of tags cannot state. Unlike the tags above there is nothing to report a change, so a
 * rule written this way is settled when it is read and does not follow the fight until it is read again.
 */
export function runsWhen(Condition: Condition): RunCondition {
	return { Kind: "OnlyWhen", Condition };
	// ▸ A non-tag condition on "stamina is 0" goes stale between reads.
}
```

This reasoning is recorded in [ADR 0038](docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md) (accepted 2026-09-24), which names Hora's flurry as the motivating case.

**Where `== 0` gives the wrong answer**

Health's floor is 1, not 0. Stamina's happens to be 0:

```ts
// Resources.GameplayAttribute.ts:94
/** Current health owns the last-point floor that keeps a participant alive until knockdown. */
export const Health = createAddressedResourceAttribute({
	// ...
	LowerLimit: floorAt(attributeAmount(1)),
	// ▸ Empty health reads 1, never 0.
	// ...
	EmptyTag: StateResourceEmptyHealth,
});
/** Current stamina owns only the live amount; its maximum is another declaration's derived value. */
export const Stamina = createAddressedResourceAttribute({
	// ...
	LowerLimit: ordinaryZeroFloor,
	// ▸ Empty stamina reads 0. Only by this declaration, not by the shape of the check.
	// ...
	EmptyTag: StateResourceEmptyStamina,
});
```

The container reads the floor off the declaration ([AttributeReadingRules.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayAttributes/AttributeReadingRules.ts:292)):

```ts
// AttributeReadingRules.ts:292
export function limitForReading(attribute: AttributeDefinition, reading: AccountedReading): HoldingLimit {
	switch (attribute.LowerLimit.Kind) {
		case "NeverBelowZero":
			if (reading.Reading <= 0) {
				return { Kind: "AtZero", Reason: "OrdinaryZeroFloor" };
			}
			break;
		case "NeverBelow":
			if (reading.Reading <= attribute.LowerLimit.Floor) {
				return { Kind: "AtFloor", Floor: attribute.LowerLimit.Floor };
			}
			break;
	// ...
```

1. A fighter's Health reads 1, its lower limit.
2. `limitForReading` returns `AtFloor`; `Settle` holds `StateResourceEmptyHealth`.
3. An ability checking `ReadGameplayAttributeAmount(Health) == 0` reads 1 and decides "not empty".
4. The bar sits at its floor, tagged empty, while the ability behaves as though it isn't — holding a phase it should leave, or starting when it should refuse.

It happens for every bar whose floor isn't zero (Health, always). It doesn't happen for Stamina today, whose floor is zero — the check agrees with the tag there by coincidence of the declaration, not because the check knows the floor.

**The part where the check works**

For Stamina in Hora's flurry, and only there, `== 0` reads the same answer the tag gives: same number, same floor, same step. I have no crash or desync to show for that one case. What separates it from the rest is whether the reader's number carries its own limit: Stamina's 0 coincides with its floor today, Health's doesn't, and the phase runtime has a wait for tags but none for numbers.

**What I couldn't confirm:**
- The order within one 0.05s step between drain pulses, recovery refills, and phase wait checks, so I can't say whether a transient empty between two checks is seen or missed on either side.
- What crosses the network for attributes versus tags; ADR 0032 names phase ordinals, tags, and effects as the replicated wire truth, so I can't turn the prediction sentence in ADR 0038 into a tag-vs-check difference.
- No gate, effect condition, or cue reads an Empty tag today — the mechanism is verified, current readers beyond Hora are not.

**What decides it:** the code that moves the number is the only code that knows where its floor is, so readers ask that owner for the fact instead of re-deriving it from the number.
