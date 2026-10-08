Hora's flurry never runs code where you could write `if stamina == 0`. That's the main reason it's a tag. The flurry is declared as data: a phase that sits waiting for whichever of three events happens first. To "just check stamina" you'd need one of two things, and the design note behind this (`docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`) considered and rejected both.

**What the flurry actually is** (`src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:130-137`):

```ts
Race: firstOf(
    onInputReleased(strikeNearestForward),
    after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
    onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
),
```

**Option 1: check the bar every tick.** Rejected. The repo bans guessing state by polling. It can also be wrong between checks: stamina is drained by a separate effect every 0.1s (`HoraStaminaDrain.GameplayEffect.ts`), and something else can also spend it or regenerate it. A check that runs on its own schedule can miss the moment it hits zero, or see it a step late.

**Option 2: a new "wait for the bar to empty" event, like `onAttributeEmpty(Stamina)`.** Rejected. The ability system would need its own way to watch numbers. And only that one waiting slot would understand "empty". Ability gates ("can't use this while out of stamina"), effect conditions and visual cues each read tags, so each would need its own copy of the same check.

**What the tag gets you instead:**

- **One owner, always correct.** Every stamina change goes through one method, `recordChange` (`GameplayAttributeContainer.ts:649-662`). In that same step it puts the empty tag on or takes it off (`EmptyTag.ts`). The bar and the tag can never disagree, and nothing has to watch the bar.
- **Everything already understands tags.** Waiting phases, gates, effect conditions and cues all react to tags. One mechanism makes "empty" usable by all of them at once.
- **Prediction comes free.** The code is shared between client and server, so the client's guess that the bar is empty comes from the same change the server later confirms.
- **It isn't a stamina-only system.** Each resource bar declares its empty tag: Health, Stamina, Chakra, BlockBar and Awakening (`Resources.GameplayAttribute.ts:102-146`). Hora's cost to use it is that one `onTagAdded` line.

The fair objection is that Hora is the only thing using it today. The project rule "build the spine before the limbs" covers that: the next ability that drains Chakra, or a gate that refuses moves at zero stamina, gets it with no extra work.

One possible confusion: the empty-stamina tag isn't **Exhaustion**. Exhaustion (`Exhaustion.GameplayEffect.ts`) is a separate effect that lowers maximum stamina by 30 for 8 seconds.
