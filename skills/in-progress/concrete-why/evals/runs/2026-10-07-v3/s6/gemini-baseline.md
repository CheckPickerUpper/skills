Based on ADR 0038 (`docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`), NRO uses an `EmptyTag` for resource depletion instead of polling for `0` inside an ability for several architectural reasons:

1. **Everything already speaks tags:** The Gameplay Ability System (GAS) relies on tags for phase races (`onTagAdded`), activation gates, effect conditions (`runsWhileTagged`), and gameplay cues. By translating "stamina is 0" into a tag, every system can instantly react to the empty state without needing a separate, bespoke mechanism.
2. **Avoids tick-polling and side-effect inference:** Checking if stamina is `0` manually would require the ability to poll the attribute every tick. The repository forbids inferring state from side effects, and polling can go wrong if the check runs between changes. 
3. **Single source of truth:** The attribute container is the only owner of the Stamina number. By having the container automatically apply the `EmptyTag` the exact moment the bar hits its lower limit, the stamina value and the empty state are guaranteed to never disagree.
4. **Consistency across the board:** If the engine instead implemented an `onAttributeEmpty(Stamina)` race just for abilities, other mechanisms (like gates or visual cues) still wouldn't be able to see the "empty" state, forcing each system to grow its own copy of the logic.

By using a tag, the event becomes instantly predictable on both client and server, and integrates natively with the rest of the phase graph architecture without any extra wiring.
