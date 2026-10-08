Hora's flurry ends on a tag today, and a `stamina == 0` check would need new runtime plumbing to ask the question the tag already answers. Keep the tag.

**How Hora's flurry ends today**

Hora, the held flurry-then-strike granted on ability slot 2 by the Silver Rapier and run by the ability runtime, is declared in [Hora.Ability.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:122). Its flurry phase holds the drain effect while racing three exits: release, timeout, and the stamina-empty tag appearing:

```ts
// Hora.Ability.ts:122, the flurry phase of Hora's phase graph
bindPhase(flurryPhase, {
	Scope: [
		ownAnimation(SilverRapierHoraHold),
		ownCue(HoraFlurryCue),
		applyWhileActive(HoraStaminaDrain),
		// ▸ The drain below is on exactly while this phase runs.
	],
	// ...
	Continuation: {
		Kind: "Await",
		Race: firstOf(
			onInputReleased(strikeNearestForward),
			after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
			onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
			// ▸ Whoever wins the race, the flurry ends in the same strike.
		),
	},
}),
```

HoraStaminaDrain, the repeating effect the flurry holds, declared in [HoraStaminaDrain.GameplayEffect.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/Content/GameplayEffects/HoraStaminaDrain.GameplayEffect.ts:28), takes 2 stamina every 0.1s:

```ts
// HoraStaminaDrain.GameplayEffect.ts:28
/** Stamina each pulse of the flurry takes. */
const HORA_STAMINA_DRAIN_PER_PULSE = 2;
/**
 * Seconds between pulses. Ten pulses a second at two each is twenty Stamina a second, twice the Reference
 * Fighter's regeneration of ten (ADR 0037), so holding the flurry costs a real ten a second net.
 */
const HORA_STAMINA_DRAIN_INTERVAL_SECONDS = 0.1;
// ▸ Net drain is ~10/s against ~10/s regen, so a held flurry always bottoms out.

/** Takes two Stamina, every tenth of a second. */
const EachPulse: RepeatingEffectAction = repeatingAction(
	modifiesNumber({
		Attribute: Resources.Stamina,
		Modification: takesAway(fixed(amountAtLeastZero(HORA_STAMINA_DRAIN_PER_PULSE))),
		Condition: Always,
	}),
);
```

Stamina, the spend-and-refill bar declaration used by costs, drains, and regen, lives in [Resources.GameplayAttribute.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/Content/GameplayAttributes/Resources.GameplayAttribute.ts:106). Each bar names its own empty tag; note health's floor is 1, not 0:

```ts
// Resources.GameplayAttribute.ts:94
/** Current health owns the last-point floor that keeps a participant alive until knockdown. */
export const Health = createAddressedResourceAttribute({
	// ...
	LowerLimit: floorAt(attributeAmount(1)),
	// ...
	EmptyTag: StateResourceEmptyHealth,
});

/** Current stamina owns only the live amount; its maximum is another declaration's derived value. */
export const Stamina = createAddressedResourceAttribute({
	// ...
	LowerLimit: ordinaryZeroFloor,
	// ▸ Stamina's floor happens to be zero. Health's is 1.
	// ...
	EmptyTag: StateResourceEmptyStamina,
});
```

`StateResourceEmptyStamina`, the binary tag meaning "stamina is at its lower limit" declared in [State.GameplayTag.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/Content/GameplayTags/State.GameplayTag.ts:211), is read by exactly one game-code site today, the flurry race above (verified by a repo-wide search in this session; the only other reader is a composition test). Its siblings cover health, chakra, block bar, and awakening, all declared the same way.

**How the tag follows the bar**

`GameplayAttributeContainer`, the per-participant owner of every kept number in [GameplayAttributeContainer.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAttributes/GameplayAttributeContainer.ts:642), settles the tag in the same step as every write, cost, and modifier change:

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
	// ▸ One funnel: no write can move a bar without re-deciding its tag.
}

/** Puts one number's Empty Tag on or takes it off to match what the number reads right now. */
private settleEmptyTag(attribute: AttributeDefinition, occurredAt: number): void {
	this.emptyTags.Settle(
		attribute,
		limitForReading(attribute, this.ledger.ReadGameplayAttribute(attribute)),
		occurredAt,
	);
	// ▸ The tag is decided from the folded reading, ceiling and gated rows included.
}
```

`ResourceEmptyTags`, the helper constructed beside the container in [composeGameplayAttributes.Shared.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAttributes/Composition/composeGameplayAttributes.Shared.ts:29) and [EmptyTag.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAttributes/EmptyTag.ts:60), holds the tag exactly while the reading rests on its lower limit, and starting bars are settled before gameplay receives the container:

```ts
// EmptyTag.ts:60
public Settle(attribute: AttributeDefinition, limit: HoldingLimit, at: number): void {
	// ...
	switch (limit.Kind) {
		case "AtZero":
		case "AtFloor":
			this.hold(marking.EmptyTag, at);
			// ▸ Bar on its floor: tag on (a second empty change adds nothing).
			return;
		case "WithinLimits":
		case "AtCeiling":
			this.tags.RemoveEveryApplicationOf(marking.EmptyTag, at, BAR_ROSE);
			// ▸ Bar above its floor: tag off.
			return;
		// ...
	}
}
```

`limitForReading`, the function in [AttributeReadingRules.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAttributes/AttributeReadingRules.ts:292) that names which limit a reading rests on, states "empty" once for every bar: at-or-below the floor, checked before the ceiling:

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
				// ▸ Health at 1 lands here. A `== 0` test never would.
				return { Kind: "AtFloor", Floor: attribute.LowerLimit.Floor };
			}
			break;
		// ...
```

This is the design recorded in `docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md` (accepted 2026-09-24): the container already performs every change, so it states "empty" in that same change.

**What a `stamina == 0` check inside the flurry would need**

The phase graph cannot read numbers today. `ActivationOwner`, the facts interface in [PhaseGraphExecutionHost.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAbilities/PhaseGraphExecutionHost.ts:139) that bounds everything a running phase may ask about its fighter, exposes two members:

```ts
// PhaseGraphExecutionHost.ts:139
/** Facts about the fighter running the ability: tags it carries and how fast its paced waits run. */
export interface ActivationOwner {
	readonly ReadTagPresence: (queryTag: GameplayTagDefinition) => GameplayAbilityTagPresence;
	readonly ReadWaitPace: (wait: AfterWait) => number;
	// ▸ No attribute read. The execution owner one layer down can read them;
	// ▸ the graph is fenced off from them.
}
```

`PhaseGraphExecution`, the stepper in [PhaseGraphExecution.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayAbilities/PhaseGraphExecution.ts:584) that evaluates each phase's race, resolves the flurry's third arm with the existing tag read:

```ts
// PhaseGraphExecution.ts:584, inside checkWaitTriggered
case "OnTagAdded": {
	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
	// ▸ Present means empty now; the transition fires on this step.
	switch (presence.Kind) {
		case "Present":
			return { Kind: "WaitTriggered", Transition: wait.Transition };
		case "Absent":
			return AwaitingEventPending;
		// ...
```

A stamina check would therefore need a fourth arm kind plus the plumbing: a new wait constructor beside `onTagAdded`, a new `ActivationOwner` member, owner-side wiring, and a prediction story for that read. Against that, the tag's marginal wiring is one declaration line per bar plus the already-built `Settle` call. Concretely, the check breaks in three places:

1. It states the wrong condition. `== 0` coincides with `limitForReading` only for zero-floor bars. Copied to health, the failure runs:
   1. Health sits at 1, its declared floor.
   2. The copied check asks `health == 0` and gets false.
   3. The ability behaves as if the bar were fine — holding a drain past empty or refusing to end early — while the bar shows its last point.
   
   This happens for any bar with a nonzero floor and never for stamina as declared today; the tag reads the declaration instead of restating it.

2. Every other consumer restates it again. Activation gates take tag queries (`Gate: onlyIf(CanUseAbilities)` on Hora itself), and effect gates already distinguish the two paths in [GameplayCondition.ts](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/ReplicatedStorage/GameplayDeclarations/GameplayCondition.ts:399):

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
}

/**
 * Writes down what has to stay true of the fight for a rule to keep acting on somebody.
 *
 * For facts a set of tags cannot state. Unlike the tags above there is nothing to report a change, so a
 * rule written this way is settled when it is read and does not follow the fight until it is read again.
 */
export function runsWhen(Condition: Condition): RunCondition {
	return { Kind: "OnlyWhen", Condition };
}
```

A "refuse sprint while stamina is empty" gate or a "pause this drain while empty" effect condition can be one tag term today; the numeric version needs a new gate/condition kind per consumer, each restating the floor rule. Sized honestly: no gate, cue, or condition reads the stamina-empty tag yet, so this leg is about the next consumer, not existing ones.

3. Sampling can hide a transient empty — but this leg does not separate the two options, so I am not counting it. The shape the ADR's rejected note stands for: drain pulses land every 0.1s while [ParticipantResources](/home/ozzy-desktop/dev/NRO-concrete-why-bench/src/Shared/Server/Participant/ParticipantResources.Server.ts:37) refills stamina every 0.05s, so a drain taking the bar to 0 followed by a refill to ~0.5 before the flurry's next step leaves a level check reading 0.5 and burning another pulse after running dry. The tag presence sampled at that same step reads Absent too, since the refill settled it off — `OnTagAdded` is a presence read, not an edge — so timing alone is not a reason to prefer it.

**What I couldn't confirm:** whether tag changes fan out into an immediate ability step (which would restore timing as a differentiator) — the only `Advance` caller I found is a test, and I did not trace a live tag-to-step path; the notification wiring behind "re-read the moment tags move" — I verified the comment and the pull sites that re-read gates, not a push mechanism; and the exact per-tick order of refill vs drain vs ability steps in one simulation tick.

**What decides it:** empty is stated once, by the owner that moves the number — readers that already read tags read it there instead of restating the floor at every site.
