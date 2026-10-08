Short answer: because "the bar is empty" is a fact many systems need, and only one place can own it correctly. ADR `docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md` records the decision.

**Why not `stamina == 0` inside Hora's flurry**

1. **Polling is racy and forbidden.** Checking inside the flurry means polling every tick and inferring state from a side effect — explicitly rejected in the ADR and against the repo rule "never guess or infer state from side effects." Stamina regenerates (10/sec for the Reference Fighter), so "is it exactly 0 right now?" is a transient condition that can be missed or observed between changes depending on tick order. The tag is set *in the same change* that takes the bar to its floor (`GameplayAttributeContainer.settleEmptyTag`, `src/Shared/ReplicatedStorage/GameplayAttributes/GameplayAttributeContainer.ts:652-656`), so the number and the tag can never disagree.

2. **One owner, one mechanism.** The attribute container already owns every change to the number, so it's the only place that knows the exact moment the bar hits its lower limit. Hora reading the value directly would be a second reader re-deriving the same fact — exactly the "1 fact, 2 owners" drift pattern.

3. **Everything already speaks tags.** Phase races (`onTagAdded`), activation gates, effect conditions (`runsWhileTagged`) and gameplay cues all read tags today. As a tag, "empty" is instantly usable by all of them. A Hora-local `== 0` check fixes only Hora; the next ability, a gate refusing block, a HUD cue, or `HoraStaminaDrain`-style conditions (`runsWhileTagged`) would each grow its own copy. The rejected alternative in the ADR — `onAttributeEmpty(Stamina)` as a special race — had the same problem: the ability runtime would grow its own attribute-watching mechanism while gates and cues still couldn't see "empty".

4. **It's predicted.** The container is shared code (ADR 0012), so the client's guess at "empty" comes from the same change the server confirms — the flurry's early strike predicts cleanly instead of waiting on a server round trip.

5. **It's per-bar and free everywhere else.** Every resource declares its `EmptyTag` (`Resources.GameplayAttribute.ts` — stamina, chakra, health, block bar, awakening), so all five bars get the same capability from one implementation. The glossary in `CONTEXT.md` even names "Empty Tag" as the vocabulary and bans "exhausted flag / out-of-stamina state" as stand-ins.

In Hora it costs one race line — `onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward)` (`Hora.Ability.ts:135`) — which is simpler than owning the check, and it can't be wrong about *when* the bar emptied.
