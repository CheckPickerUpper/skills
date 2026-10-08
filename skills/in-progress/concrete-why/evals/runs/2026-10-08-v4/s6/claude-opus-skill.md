You can't write "check if stamina is 0" inside Hora's flurry today, because the flurry has no code body. It is a list of waits. The only waits on offer are for a tag, input, time and a few other events, and none of them reads a number. So the "simple check" would actually mean adding a new kind of wait to the ability runtime. The empty-stamina tag needs no new wait: Hora uses the existing `onTagAdded` wait in one line. Keep the tag.

One thing first: the tag Hora reacts to is `StateResourceEmptyStamina`, not `Exhaustion`. `Exhaustion` (`Content/GameplayEffects/Exhaustion.GameplayEffect.ts`) is a separate effect that lowers maximum stamina by 30 for 8 seconds. Hora never touches it.

**What the flurry is today**

`Hora.Ability.ts` declares Hora as phases: windup, flurry, strike, recovery. Each phase waits on a race of events, and the first event to happen picks the next phase. Here is the flurry:

```ts
// Hora.Ability.ts:122
bindPhase(flurryPhase, {
	Scope: [
		ownAnimation(SilverRapierHoraHold),
		ownCue(HoraFlurryCue),
		applyWhileActive(HoraStaminaDrain),
		// ▸ Drains 2 Stamina every 0.1 s for as long as this phase runs.
	],
	// ...
	Continuation: {
		Kind: "Await",
		Race: firstOf(
			onInputReleased(strikeNearestForward),
			// ▸ Player lets go → strike.
			after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
			// ▸ 1.5 s pass → strike.
			onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
			// ▸ Stamina's empty tag appears → strike.
		),
	},
}),
```

`PhaseGraph.ts` defines the waits a race can hold: `after`, `onInputReleased`, `onInputPressed`, `onOwnerDied`, `onTagAdded`, `onTagRemoved`, `onIncomingAttack`, `onAttackFinished` and `onTargetLost`. None of them reads an attribute such as Stamina.

**What the tag needs (already built)**

The attribute container (`GameplayAttributeContainer.ts`) is the shared code that changes every bar's number. Every write, cost and modifier change ends up in one function, and that function sets or clears the bar's empty tag in the same step:

```ts
// GameplayAttributeContainer.ts:649
private recordChange(change: GameplayAttributeChange): void {
	this.versions.RecordChange(change.Attribute);
	writeAttributeChange(this.log, change);
	this.settleEmptyTag(change.Attribute, change.OccurredAt);
	// ▸ Puts StateResourceEmptyStamina on if Stamina is now 0, takes it off if it's above 0.
}
```

`ResourceEmptyTags.Settle` (`GameplayAttributes/EmptyTag.ts:60`) does the putting on and taking off. Stamina names its tag where it is declared (`Resources.GameplayAttribute.ts:113`, `EmptyTag: StateResourceEmptyStamina`). Health, Chakra, Block Bar and Awakening each declare one too. All of this exists today, so Hora's use of it costs the one `onTagAdded` line.

**What "just check stamina is 0" would need**

There is nowhere in Hora to put an `if`, so you would add a wait kind, something like `onAttributeEmpty(Stamina)`. That means:

1. A new wait type and builder in `PhaseGraph.ts` and `GameplayAbility.Types.ts`.
2. A new case in each of the four switches over wait kinds in `PhaseGraphExecution.ts` (the runtime that steps each phase), at lines 63, 490, 532 and 584. They are exhaustive, so it won't compile until all four handle it.
3. A new way for the runtime to read the owner's attributes. Today the waits only call `this.host.Owner.ReadTagPresence(...)`.

That is more code than the tag path, not less. ADR 0038 (`docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`, the decision record behind the tag) lists this exact option and rejects it.

**Where the tag's case is weaker than its record says**

- **The "polling goes wrong" argument doesn't apply here.** ADR 0038 also rejects polling the bar every tick because "it goes wrong whenever the check runs between changes." But `onTagAdded` is itself checked by polling. On every `Advance` step, the runtime reads whether the tag is present:

  ```ts
  // PhaseGraphExecution.ts:584
  case "OnTagAdded": {
  	const presence = this.host.Owner.ReadTagPresence(wait.Tag);
  	// ▸ Read on each Advance step, not pushed when the tag goes on.
  	switch (presence.Kind) {
  		case "Present":
  			return { Kind: "WaitTriggered", Transition: wait.Transition };
  ```

  The tag is set in the same change that moves the number, so reading "Stamina is 0" at that same moment would give the same answer. For Hora, a stamina-reading wait would strike on exactly the same step. The real advantage of the tag is that it needs no new wait kind, not that it times anything better.

- **"Everything already reads tags" is mostly future benefit.** The ADR's main reason is that activation gates, effect conditions and cues all read tags, so an empty bar becomes visible to all of them for free. Today, the only game code that reads `StateResourceEmptyStamina` is Hora's flurry. Apart from that, only `AttributeComposition.integration.ts` reads the stamina tag. No gate, cue or condition uses it yet. The project's own rule ("build the spine before the limbs" in `CLAUDE.md`) accepts building it before those users exist, but it shouldn't be counted as savings already made.

**What I couldn't confirm:** I didn't run Hora to watch it strike the moment stamina hits 0. The same-step timing above comes from reading `recordChange` and `checkWaitTriggered`, not from a test run.

**What decides it:** does the flurry have somewhere to put an `if`? It doesn't. Its only way to react is a wait in the race, and a tag wait already exists while an attribute wait does not.
