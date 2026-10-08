Short version: a check inside Hora's Flurry would only look at stamina when something asks it to. The ability needs to be told the moment stamina runs dry, and a tag does that.

**What the code does today**
- Hora's flurry races three endings (`Hora.Ability.ts:132-136`): the button is released, the max hold time passes, or `onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward)` fires.
- The flurry drains stamina through the `HoraStaminaDrain` effect while it's held. The drain is what pushes stamina to 0, so the end of the flurry has to be driven by that moment of reaching 0.

**Why a tag instead of an `if stamina == 0`**
1. **It's an event, not a poll.** The flurry is waiting in a race. An `if` has to run at some moment, so you'd be polling stamina every tick. The tag turns "stamina hit 0" into something the race can wait on. `onTagAdded` fires the instant it happens.
2. **The tag and the number can't disagree.** The doc comment on `HoldsEmptyTag` in `GameplayAttribute.Types.ts:291-299` says the attribute container adds the tag in the same change that moves the number. So there's no window where stamina is 0 but the tag isn't set yet.
3. **It's not a stamina-specific or Hora-specific tag.** Every bar (health, chakra, stamina) declares an Empty Tag. That's the general form. Anything else that reacts to a bar running dry reads the same tag: gates that refuse an action, cues that show exhaustion, other held abilities. The project's "build the spine before the limbs" rule in `CLAUDE.md` pushes toward this shape. A per-ability `stamina == 0` check would be rebuilt in each consumer.
4. **It follows the project's "take the dependency" rule.** The ability names the declared tag (`Resources.Stamina.WhileEmpty.EmptyTag`) directly. It doesn't infer state by polling a number. It's also the same shape the other endings use (`onInputReleased`, `after`).

**The cost is small.** The tag is declared once per bar (`StateResourceEmptyStamina` in `State.GameplayTag.ts:212`), and the attribute declaration supplies it. Hora only adds the one `onTagAdded` line.

If you'd rather have a direct stamina check, it would have to live in the flurry's tick or in the drain effect. That duplicates the logic per ability and creates a gap between the number and what the ability sees. I'd keep the tag.
