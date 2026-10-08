Short answer: it was decided in `docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`, and the "simpler" check is actually the bigger mechanism.

**Why the check isn't simpler**

Hora's flurry has no code to put the check *in*. The ability is declarative phase-graph content (`src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts`): the flurry phase is an `Await` race of `onInputReleased` / `after(...)` / `onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward)`. There is no per-tick loop to write `if stamina == 0`. To support that you'd have to add either:

- a new phase race that watches attributes (`onAttributeEmpty(Stamina)`) — a second observation mechanism in the ability runtime, alongside the tag system gates, cues and effect conditions (`runsWhileTagged`) already use, or
- a per-tick poll — which the repo explicitly forbids ("never guess or infer state from side effects", `AGENTS.md`), and which is racy: it misses the empty moment if it doesn't happen to run between the change and the next drain pulse, and forces you to pick a check rate.

The tag costs one line in the flurry's existing race. The "simple check" costs a brand-new mechanism only Hora could use.

**Why the tag is the right owner**

- **One owner of the fact.** The attribute container is the only thing that performs the bar change, so it's the only place that knows the instant the bar hits its lower limit. It sets/clears the tag in that same change (`GameplayAttributeContainer.settleEmptyTag` → `ResourceEmptyTags` in `src/Shared/ReplicatedStorage/GameplayAttributes/`), so the number and the tag can never disagree. If Hora checked `Stamina == 0` itself, every consumer would re-encode the boundary semantics (zero exactly? below? rounding?).
- **Everything already speaks tags.** Activation gates, effect conditions and gameplay cues can all see "empty" for free. With a Hora-local check, each of those would grow its own copy.
- **It's predicted like everything else.** The container is shared code (ADR 0012), so the client's guess at "empty" is the same change the server confirms — `onTagAdded` fires consistently on both machines. A hand-rolled check in the flurry would have to reimplement that prediction seam.
- **It generalizes to every bar, not just stamina.** All five resources declare an `EmptyTag` (`Resources.GameplayAttribute.ts`): health, stamina, chakra, block bar, awakening. Any future held drain — chakra channels, block break, awakening burn — reacts the same way with zero new machinery.

ADR 0038 also names the rejected alternative you're proposing almost verbatim ("Polling the bar from the ability every tick"), so this is a recorded decision, not an accident.
