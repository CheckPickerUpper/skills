Short version: Hora's flurry isn't code that runs every tick, so there's nowhere for an "if stamina is 0" check to live. The flurry is an `Await` phase that waits on a race of events, so it needs something to fire when stamina hits zero. The tag is that event.

**How it works now**
- The flurry phase races three endings: the button is released, the max hold time elapses, or `onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward)` fires (`src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:130-137`).
- `Stamina` declares `EmptyTag: StateResourceEmptyStamina` (`Resources.GameplayAttribute.ts:113`).
- `ResourceEmptyTags.Settle` in `GameplayAttributes/EmptyTag.ts` runs after every change the attribute container lands. It puts the tag on when the bar is at its lower limit and takes it off when the bar rises.

**Why not check `stamina == 0` inside Hora**

[ADR 0038, "An Empty Resource Bar Is a Gameplay Tag"](docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md) gives the reasons:
1. **Polling is the only way to check inside Hora.** Hora has no per-tick code, so it would have to poll the bar every tick. The ADR rejects that because it infers state from a side effect, which NRO's `CLAUDE.md` forbids ("Take the dependency"). It also goes wrong whenever the check runs between changes.
2. **Other systems need the same fact.** Phase races, activation gates, effect conditions (`runsWhileTagged`) and gameplay cues all read tags. A zero-check inside Hora would help only Hora. Every other ability, gate or cue that cares about empty stamina, health or chakra would need its own copy.
3. **The tag and the number can't disagree.** The attribute container is the only code that changes the number, so it sets the tag in the same step. The container is shared code (ADR 0012), so the client's prediction of "empty" matches what the server confirms.

The ADR also rejected a narrower option, `onAttributeEmpty(Stamina)`. It would have solved Hora but left gates and cues without a way to see "empty".

**What it costs**

The tag is more machinery than a one-line check, and you're right that it looks heavy for one ability. The cost is mostly paid already, because `ResourceEmptyTags` is generic and every bar gets its Empty Tag for free. If you want a simple `stamina == 0` check, the realistic route is to supersede ADR 0038, since the repo rules rule out a one-off poll in Hora.
