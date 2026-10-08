> The flurry doesn't look at the stamina number at all today. It waits on one line, `onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, ...)`, and the attribute container sets that tag in the same call that moves the number to zero. "Just check stamina inside the flurry" sounds like one line, but there is no place inside a flurry to check: a phase's hold runs on event waits, and none of the existing waits reads an attribute. Making the check possible is new ability-runtime machinery; the tag reused machinery that already existed. The check would also re-declare what "empty" means in every caller, where the container already decides it once.

**What happens today when the flurry drains stamina to zero**

`HoraStaminaDrain` (the repeating gameplay effect the flurry phase holds active, `src/Shared/ReplicatedStorage/Content/GameplayEffects/HoraStaminaDrain.GameplayEffect.ts`) takes 2 stamina every 0.1 s. Each pulse is a change landed by `GameplayAttributeContainer` (the one shared class that owns every attribute write, `src/Shared/ReplicatedStorage/GameplayAttributes/GameplayAttributeContainer.ts`). Every landing ends here:

```ts
// GameplayAttributeContainer.ts:649, inside recordChange — reached by every write, cost and modifier
private recordChange(change: GameplayAttributeChange): void {
	this.versions.RecordChange(change.Attribute);
	// ▸ Bumps the change counter other surfaces poll.
	writeAttributeChange(this.log, change);
	this.settleEmptyTag(change.Attribute, change.OccurredAt);
	// ▸ In the same call, sets or takes off the bar's Empty Tag to match the new number.
}
```

`settleEmptyTag` asks `ResourceEmptyTags` (the per-participant keeper of bars' Empty Tags, `src/Shared/ReplicatedStorage/GameplayAttributes/EmptyTag.ts`), which decides "empty" from where the number now rests:

```ts
// EmptyTag.ts:71, inside ResourceEmptyTags.Settle
switch (limit.Kind) {
	case "AtZero":
	case "AtFloor":
		this.hold(marking.EmptyTag, at);
		// ▸ Bar is at its lower limit: put the tag on, unless it is already on.
		return;
	case "WithinLimits":
	case "AtCeiling":
		this.tags.RemoveEveryApplicationOf(marking.EmptyTag, at, BAR_ROSE);
		// ▸ Bar rose again: take the tag off.
		return;
```

The flurry's hold phase then ends on that tag:

```ts
// Hora.Ability.ts:126, inside bindPhase(flurryPhase, ...)
Scope: [
	// ...
	applyWhileActive(HoraStaminaDrain),
	// ▸ Keeps the drain effect running exactly while the hold runs.
],
Continuation: {
	Kind: "Await",
	Race: firstOf(
		onInputReleased(strikeNearestForward),
		after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
		onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
		// ▸ Strikes early when the bar runs dry — reads the tag, not the number.
	),
},
```

One correction to the picture in the question: `onTagAdded` is not a subscription that can miss a moment. The runtime re-checks it every simulation tick and fires on presence, so a bar already empty when the hold starts strikes at once:

```ts
// PhaseGraphExecution.ts:584, inside checkWaitTriggered — run once per tick per open wait
case "OnTagAdded": {
	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
	switch (presence.Kind) {
		case "Present":
			return { Kind: "WaitTriggered", Transition: wait.Transition };
		// ▸ Fires whenever the tag is on, including before this phase began.
```

So the tag does not end the hold faster than a check would; both would be sampled at the same tick. What separates them is where the decision lives and who can see it.

**Why "just check inside the flurry" is not a smaller edit**

*1. There is no check hook to write the check in.*

1. The hold phase's only continuation is `Await` over a race of waits (`Hora.Ability.ts:130-137`).
2. Every wait kind is listed in the runtime's per-tick check (`PhaseGraphExecution.ts:543-618`): `After`, `OnInputPressed`, `OnInputReleased`, `OnOwnerDied`, `OnTagAdded`, `OnTagRemoved`, `OnIncomingAttack`, `OnAttackFinished`, `OnTargetLost`. Not one reads an attribute.
3. Conditions run only in phase `Enter` actions and commits, and their vocabulary has no attribute-value test either (`GameplayAbility.Types.ts:685-690`: `All`, `TargetIsValid`, `HasTargetData`, `TargetHasTag`, `CanPay`). An `Enter` check runs once when the hold starts; the drain empties the bar ~1 s later, so the flurry would never strike early and the "strikes … the moment Stamina runs dry" behavior written in its own description (`Hora.Ability.ts:176-177`) would not exist.
4. So the check means a new wait kind in `PhaseGraph.ts`, a new case in `PhaseGraphExecution`, and a new attribute read on the execution host — the ability runtime growing its own way to watch attributes. That is exactly the option `docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md` weighed and rejected; `onTagAdded` already existed, so the tag route was one line in Hora.

There is an `AttributeThreshold` branch in the older simulation-sequence types (`GameplayAbility.Types.ts:335`), but I found nothing that runs it for phase-graph abilities — see the unconfirmed line below. Even if live, it branches at a sequence step, not "the moment the bar runs dry during a 1.5 s hold".

*2. The check re-declares what "empty" means, and "is 0" is a special case.*

"Empty" is decided in one place from the bar's lower-limit declaration:

```ts
// AttributeReadingRules.ts:292, inside limitForReading
switch (attribute.LowerLimit.Kind) {
	case "NeverBelowZero":
		if (reading.Reading <= 0) {
			return { Kind: "AtZero", Reason: "OrdinaryZeroFloor" };
		}
		break;
	case "NeverBelow":
		if (reading.Reading <= attribute.LowerLimit.Floor) {
			return { Kind: "AtFloor", Floor: attribute.LowerLimit.Floor };
			// ▸ A bar can rest at a floor above zero and still count as empty.
		}
```

Today all five bars — Health, Stamina, Chakra, BlockBar, Awakening (`src/Shared/ReplicatedStorage/Content/GameplayAttributes/Resources.GameplayAttribute.ts:102-146`) — use `ordinaryZeroFloor` (Stamina at line 109), so `stamina == 0` and `AtZero` happen to agree. The failure is a numbered drift, not a current bug:

1. Balance gives Stamina (or BlockBar, whose broken state already keys off `ReducedAtFloor`, `ParticipantResources.Server.ts:228-231`) a `NeverBelow` floor of 10.
2. The container marks the bar `AtFloor` at 10 and the Empty Tag goes on (`EmptyTag.ts:73-74`).
3. Hora's hand check `stamina == 0` never fires; the flurry keeps holding past the point every ledger change reports as the bar resting at its floor.

*3. A check gives only Hora the fact; a tag gives it to every tag reader at once.*

Activation gates, effect conditions (`runsWhileTagged`, the gated-modifier mechanism ADR 0037 prices buffs on) and gameplay cues read tags today — `hasTag` is the whole condition vocabulary for possession (`src/Shared/ReplicatedStorage/GameplayDeclarations/GameplayCondition.ts:470`). If "empty" were a number test, each of those that ever needs "the bar is empty" grows its own attribute read or a new condition kind, one per surface, while the tag makes it `hasTag(Chakra.WhileEmpty.EmptyTag)` and nothing new. Hora is today the only reader of any Empty Tag (I grepped: `Hora.Ability.ts:135` plus `AttributeComposition.integration.ts`), so these consumers "can" arrive rather than "will" — the repo's rule is to build the spine before the limbs.

**What the tag costs**

`EmptyTag.ts` (one ~115-line class, constructed once per participant at `composeGameplayAttributes.Shared.ts:29`), one `EmptyTag: StateResourceEmptyStamina` field on each of the five bar declarations, and one call in `recordChange`. Each empty/fill transition adds one tag grant or removal; the `hold` path skips it when the tag is already on (`EmptyTag.ts`, `hold`'s presence check), so it is per transition, not per drain pulse. All of it is shared code, so the client's predicted "empty" and the server's settle come from the same write.

**What I couldn't confirm**

- Whether anything executes the `AttributeThreshold` simulation branch. Grep found only two visitors that classify it while walking sequences (`GameplayAbilitySequenceSearch.ts:44`, `GameplayAbilityInitialCosts.ts:59`), no executor.
- Whether any gate, cue or second ability will actually read the Empty Tags; the ADR names them as intended consumers, and today only Hora and one integration test reference them.

**What decides it:** does only the ability draining a bar ever need to know the bar is empty? If yes, a check would serve, once the runtime grows somewhere to put it. The moment a second surface needs the fact, one shared declaration with one definition of "empty" beats N per-caller checks — and the mechanism is already paid for across all five bars.
