**Short answer:** Stamina reaching zero is a tag because Hora's flurry has to end the moment a drain pulse empties the bar. Nothing inside the flurry runs between pulses to check, so an `if (stamina == 0)` has nowhere to sit. The tag costs one line in Hora, because the stamina code already puts it on and takes it off for every bar. I don't recommend replacing it.

**What exists today**

Hora is the Taijutsu ability in `src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts`. Its flurry phase is a waiting phase: it declares a race and does nothing else until one entry wins (`Hora.Ability.ts:130-137`).

```ts
Continuation: {
	Kind: "Await",
	Race: firstOf(
		onInputReleased(strikeNearestForward),
		// ▸ The player lets go of the button.
		after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
		// ▸ The 1.5-second hold runs out.
		onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
		// ▸ The Stamina-empty tag appears on the fighter. This is the only line the tag costs Hora.
	),
},
```

The drain is a separate effect, `HoraStaminaDrain` (`HoraStaminaDrain.GameplayEffect.ts`). It takes 2 Stamina every 0.1 s while the flurry phase is active. Hora's own code never touches the stamina number during the flurry.

The tag is `StateResourceEmptyStamina` (`State.GameplayTag.ts:212`). `Resources.Stamina` declares it at `Resources.GameplayAttribute.ts:113`. The code that keeps it correct is in `GameplayAttributes/EmptyTag.ts` and `GameplayAttributeContainer.ts:649`:

```ts
// GameplayAttributeContainer.ts:649
private recordChange(change: GameplayAttributeChange): void {
	this.versions.RecordChange(change.Attribute);
	writeAttributeChange(this.log, change);
	this.settleEmptyTag(change.Attribute, change.OccurredAt);
	// ▸ After every landed change, the bar's tag goes on if it is at its lower limit and off if it is not.
}
```

Every stamina write, cost, and modifier goes through that function. A drain pulse that takes Stamina to 0 therefore adds the tag in the same step. The flurry's wait sees it and starts the strike.

**What an inline "is stamina 0" check would need**

1. `HoraStaminaDrain` lowers Stamina by 2 and lands the change. Stamina is now 0.
2. The flurry phase is only waiting on its race. It has no code that runs after a pulse.
3. A zero check would have to be written into the race, into the drain effect, or into a per-tick poll.
   - **In the race:** there is no race entry that reads a number, so you would add a new kind, such as `onAttributeEmpty(Stamina)`.
   - **In the drain effect:** the effect would have to reach into the ability and end the phase. That is the wiring the repo avoids by having the ability wait on a fact instead.
   - **Per-tick poll:** the check runs on the next tick, not at the pulse that emptied the bar.

ADR 0038 (`docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`) rejects both of those. The race entry would give Hora a stamina watcher while gates, cues, and effect conditions still could not see "empty". Polling it rejects as inferring state from a side effect, which the repo forbids.

**Consequences of the tag approach**

- **The client predicts it:** the stamina container is shared code that runs on client and server (ADR 0012). The client's guess at "empty" comes from the same change the server confirms. Hora's prediction is `WaitsForServer`, so Hora doesn't use this today; the benefit is for abilities that predict.
- **It's already built for every bar:** health, stamina, chakra, block bar, and awakening each declare an empty tag (`Resources.GameplayAttribute.ts:102-146`). Only Hora reads one today. I checked: `onTagAdded` appears in exactly two places in game content, Hora and the M1 string (which waits on stun tags), and nothing queries the empty tags in gates or effect conditions yet.
- **A fighter who is already empty:** the wait checks tag presence when it starts (`PhaseGraphExecution.ts:584-593`). If the tag is already on, it fires at once. A one-shot "stamina just hit zero" event would miss that case.

**What I couldn't confirm:** the ADR names gates, cues, and effect conditions as readers of the empty tag. I found no content that does this today, so that benefit is planned and not used.

**What decides it:** an inline check works only if code runs at the exact moment stamina changes. The tag is set at that moment by the one place that changes the number, so any waiting ability just has to ask for it.
