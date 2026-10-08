The flurry never compares the number itself — the attribute container flips the tag in the same step it lands the change that empties the bar, and the flurry races against the tag beside its two sibling waits. Checking the number inside the flurry isn't simpler: the flurry has nowhere to put a check without teaching the ability runtime to watch attributes, the comparison re-declares "empty" and gets it wrong for a bar that exists today (Health's lower limit is 1, not 0), and the fact becomes invisible to every reader except this one ability.

**How a held flurry ends today**

`Hora` (`src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts`, the rapier's heavy thrust: press pays 20 stamina, hold a flurry, strike forward) spends its hold phase waiting on three events:

```ts
// Hora.Ability.ts:121, the flurry hold phase of Hora's phase graph
bindPhase(flurryPhase, {
	Scope: [
		ownAnimation(SilverRapierHoraHold),
		// ...
		applyWhileActive(HoraStaminaDrain),
		// ▸ Attaches a repeating effect to the fighter: 2 stamina taken every 0.1 s
		//   (HoraStaminaDrain.GameplayEffect.ts:27-38), 20 a second against 10 a second regenerated.
	],
	Continuation: {
		Kind: "Await",
		Race: firstOf(
			onInputReleased(strikeNearestForward),
			// ▸ The button was let go.
			after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
			// ▸ The hold ran its full 1.5 seconds.
			onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
			// ▸ Stamina reached its lower limit. All three take the same exit: strike the nearest fighter forward.
		),
	},
}),
```

`StateResourceEmptyStamina` (`src/Shared/ReplicatedStorage/Content/GameplayTags/State.GameplayTag.ts:211`, one of five Empty Tags — every bar of health, stamina, chakra, block bar and awakening declares one at `Resources.GameplayAttribute.ts:102-146`) is not set by Hora. `GameplayAttributeContainer` — the class that owns each participant's attribute numbers and lands every write, cost and modifier — settles it inside the change itself:

```ts
// GameplayAttributeContainer.ts:648, the one place every attribute change lands
private recordChange(change: GameplayAttributeChange): void {
	this.versions.RecordChange(change.Attribute);
	writeAttributeChange(this.log, change);
	this.settleEmptyTag(change.Attribute, change.OccurredAt);
	// ▸ Flips the bar's Empty Tag in the same step the number moved, so the two cannot disagree.
}
```

```ts
// EmptyTag.ts:66, ResourceEmptyTags.Settle — called once per landed change and once per participant build
switch (limit.Kind) {
	case "AtZero":
	case "AtFloor":
		this.hold(marking.EmptyTag, at);
		// ▸ The bar rests on its lower limit: put the tag on, if it is not on already.
		return;
	case "WithinLimits":
	case "AtCeiling":
		this.tags.RemoveEveryApplicationOf(marking.EmptyTag, at, BAR_ROSE);
		// ▸ The bar is off its lower limit: take the tag off.
```

**What "check stamina inside the flurry" would actually take**

A phase's continuation is a `firstOf` race of `GameplayWait` values, and the wait vocabulary is nine fixed kinds (`GameplayAbility.Types.ts:584-645`): `After`, `OnInputReleased`, `OnInputPressed`, `OnOwnerDied`, `OnTagAdded`, `OnTagRemoved`, `OnIncomingAttack`, `OnAttackFinished`, `OnTargetLost`. None reads an attribute. So "check inside the flurry" has two possible shapes:

1. A new wait kind (`onAttributeEmpty(Stamina)`): a new case in each of the four exhaustive wait switches in `PhaseGraphExecution` (the phase-graph stepper shared by every ability — `PhaseGraphExecution.ts:63`, `:490`, `:532`, `:584`), plus a second way for abilities to observe the world. This is exactly the option ADR 0038 (`docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`) rejected, and its reason survives translation: activation gates, gameplay cues and effect conditions read tags today — Hora's own activation gate is `onlyIf(CanUseAbilities)`, one of five tag queries in `State.GameplayTag.Queries.ts:25-94` — and none of them has an attribute-watching mechanism, so each would grow its own reader.
2. Per-tick code inside the ability that samples the number: `AGENTS.md` ("Take the dependency") forbids inferring state from polling and closures that disguise missing wiring, and the flurry declaration is data — there is no hook in a phase spec to hang a check on.

**The check re-decides what "empty" means, and one bar already breaks it**

"Empty" is not "the number reads 0". It is "the number rests on its declared lower limit", and that limit is a declaration (`NeverBelowZero`, `NeverBelow`, `NoFloor` — `GameplayAttribute.Types.ts:253-259`) consulted in exactly one place:

```ts
// AttributeReadingRules.ts:292, limitForReading
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
```

```ts
// Resources.GameplayAttribute.ts:94, the health bar — one of the five bars that declares an Empty Tag
export const Health = createAddressedResourceAttribute({
	// ...
	LowerLimit: floorAt(attributeAmount(1)),
	// ▸ Health never goes below 1: the last point that keeps a fighter standing until knockdown.
	EmptyTag: StateResourceEmptyHealth,
	// ▸ And it still declares an Empty Tag — "empty" here means resting on 1.
});
```

What goes wrong when the flurry's pattern is written as a comparison:

1. A fighter is beaten to their floor: 1 health. `recordChange` settles `StateResourceEmptyHealth` — the bar is at its lower limit.
2. A knockdown reaction is authored the way the flurry check would be: `if health === 0`.
3. Health reads 1. The comparison is false and the reaction never runs, while the tag that says "this bar bottomed out" is on the whole time.

And for stamina itself, the comparison *can* rot rather than being wrong from birth: `LowerLimit` already supports `NeverBelow` on any attribute and the ledger classifies `ReducedAtFloor` changes (`AttributeLedger.Types.ts:166`), so a buff that floors stamina at, say, 10 leaves a held flurry pressing the bar to 10 and stopping there — `=== 0` reads 10 at every step and never fires, so the flurry plays its full 1.5 s and strikes on the hold timer instead of the moment the bar bottomed out. With the tag, `Settle` sees `AtFloor` and holds it. That scenario rests on future content using `floorAt` for stamina; today stamina's floor is `ordinaryZeroFloor` (`Resources.GameplayAttribute.ts:108`).

**The fact stops being visible to anything but Hora**

1. Later, a gate ("cannot start a chakra ability with an empty chakra bar"), an effect condition, or a cue (the fighter gasps when the bar runs dry) is authored. All three read tags today.
2. The only place "stamina ran out" exists is a comparison inside Hora's flurry phase. None of the three can see it.
3. Each writes its own comparison of its own bar to its own idea of empty — the copies from the bug above, one per consumer.

Two things the tag carries that a number cannot: its grant is recorded with a cause (`GameOwnedCause("ResourceEmptied")` — `EmptyTag.ts:87`), so the causal flight log (ADR 0026) shows when and why the fighter ran dry; and a blocker can keep it off deliberately:

```ts
// EmptyTag.ts:98, inside ResourceEmptyTags.hold
switch (placed.Kind) {
	case "Granted":
		return;
	case "Blocked":
		// Something on the participant keeps this tag off, which is that blocker's decision to make.
		return;
```

That is the seam a "relentless: flurry does not end when stamina runs dry" effect plugs into — block `StateResourceEmptyStamina`. With a numeric check, suppression becomes a bespoke flag per ability.

**"Way simpler than a whole tag" miscounts the work**

The tag machinery is written once for all five bars (`EmptyTag.ts:48`, one call site at `GameplayAttributeContainer.ts:652`); in the flurry it is the one wait line shown above, inside a race that already holds two sibling waits. The alternative is not zero machinery: it is the new wait kind plus four switch cases plus one comparison per consumer — or a polling hook the declaration format does not have. `AGENTS.md` ("Build the spine before the limbs") addresses the "only Hora reads it today" version of this objection directly.

**What the tag does not buy here**

Timing. `OnTagAdded` is evaluated as a presence read at the flurry's phase step:

```ts
// PhaseGraphExecution.ts:584
case "OnTagAdded": {
	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
	switch (presence.Kind) {
		case "Present":
			return { Kind: "WaitTriggered", Transition: wait.Transition };
```

So on stamina today, a numeric check placed at that same step would fire on the same step. The tag is not faster for this one race; its case rests on ownership of the "empty" rule and on every other reader being able to see the fact.

**What I couldn't confirm**

- No test connects the two halves: `AttributeComposition.integration.ts` asserts the Empty Tags go on at the lower limit, and `SilverRapierPractice.integration.ts` covers the flurry's release and full-hold exits, but I found no test that drains stamina mid-flurry and asserts the early strike.
- ADR 0038 says gates, cues and conditions read the Empty Tag. Today none does — the only readers of any Empty Tag in game code are `Hora.Ability.ts:135` and the two assertions in `AttributeComposition.integration.ts`. Those wider consumers are the "spine before limbs" bet from `AGENTS.md`, not a verified fact.

**What decides it:** "empty" is the bar resting on a lower limit that only the attribute container's declaration knows (`NeverBelowZero`, `NeverBelow`, `NoFloor`); a consumer comparing the number re-declares that rule in every copy, and shows the fact to nobody but itself.
