The tag is there because Hora's flurry is declared as data, and the only way a flurry like that can react to anything is by waiting for an event. A plain "is Stamina 0?" check would have nothing to run inside. [ADR 0038, "An Empty Resource Bar Is a Gameplay Tag"](docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md) records the decision. I found no code that conflicts with it.

**How Hora's flurry ends today**

Hora is a declared phase graph in `Hora.Ability.ts`. Its flurry phase is a race between three ways to end (`Hora.Ability.ts:130`):

```ts
Continuation: {
	Kind: "Await",
	// ▸ The phase just waits. There is no per-tick function to put an `if` in.
	Race: firstOf(
		onInputReleased(strikeNearestForward),
		// ▸ The player let go of the button.
		after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
		// ▸ The 1.5 second hold ran its full length.
		onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
		// ▸ Stamina ran dry.
	),
},
```

Every arm of the race is an event the game announces. The wait types in `PhaseGraph.ts:184-279` are `after`, `onInputReleased`, `onInputPressed`, `onOwnerDied`, `onTagAdded`, `onTagRemoved` and `onIncomingAttack`. I found no wait that watches a number, so "Stamina is 0" has to become an event before the flurry can see it.

**Where the tag comes from**

The flurry drains Stamina through the effect `HoraStaminaDrain`, which takes 2 Stamina every 0.1 seconds. Each change to a bar passes through `recordChange` in `GameplayAttributeContainer.ts:649`:

```ts
this.versions.RecordChange(change.Attribute);
writeAttributeChange(this.log, change);
this.settleEmptyTag(change.Attribute, change.OccurredAt);
// ▸ Right after the number moves, the container asks whether the bar now sits at its lower limit.
// ▸ If it does, `ResourceEmptyTags.Settle` (EmptyTag.ts:60) puts the "Stamina empty" tag on the fighter.
// ▸ If it doesn't, the tag comes off.
```

What happens in a flurry that runs dry:
1. A drain pulse takes Stamina from 2 to 0.
2. In that same step the container adds the Stamina-empty tag.
3. The flurry's `onTagAdded` arm fires and the phase moves to the strike.

**What checking Stamina is 0 inside the flurry would mean**

The check would have to be an `if` that runs at some moment. The ability has no code that runs each tick, so something would have to call it. That means one of two things:
- Poll the bar every tick from the ability. ADR 0038 rejects this because it infers state from a side effect, which the repo forbids, and it goes wrong whenever the check runs between changes.
- Add a new wait such as `onAttributeEmpty(Stamina)`. ADR 0038 rejects this too: the ability runtime would need its own way to watch attributes, and gates, cues and effect conditions still couldn't see "empty". Each would need its own copy.

**The second reason: other things read the same tag**

The tag is a general fact, not a Hora detail. Every bar (Health, Stamina, Chakra, block bar, Awakening) declares one (`Resources.GameplayAttribute.ts:102-146`). Gates, cues and effect conditions already read tags, so an empty bar reaches all of them at once. Today only Hora's flurry consumes the Stamina one. Besides Hora, only `AttributeComposition.integration.ts` reads it, as a test.

**The third reason: prediction**

The container is shared code that runs on both the client and the server (ADR 0012). The client's guess that Stamina is empty therefore comes from the same change the server confirms.

**What I couldn't confirm**

- I did not check whether the code that runs phase graphs delivers `onTagAdded` immediately. I inferred the timing from `EmptyTag.ts`'s header comment and ADR 0038, not from that runner.
- The ADR says a check run between changes "goes wrong". It does not give the sequence of events that would go wrong, and I could not reconstruct one from the code. That ADR line is the weakest part of the argument for the tag.

**What decides it**

Can the flurry see the bar run dry without anything polling the number? Only a tag, or a new watcher built just for this, gives it an event to wait on.
