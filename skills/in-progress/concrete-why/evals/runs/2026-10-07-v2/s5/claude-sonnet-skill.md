**Short answer:** NRO hands back the removal on purpose, and subscribing would cost more than it saves. [ADR 0003, "A Mutation Returns Its Change"](docs/adr/0003-a-mutation-returns-its-change.md) rejects the Unreal-style `OnGameplayTagAdded` model by name. Subscribing is less wiring to write. The wiring you skip is what makes the other approach safe.

`RemoveGrantedTag` (`GameplayTagContainer.ts:266`) returns a `GrantedTagRemoval`. That is either `Removed`, carrying the grant and the tag's presence after the removal, or `NotActive`. The HUD gets the change as a value at the call site.

**What subscribing would break** (all four are in the ADR):

- **A bar that never greys out.** Spawn setup grants `Stunned`, and the health bar subscribes in its own init one frame later. The list of listeners is empty when the grant happens, so the bar never hears about it. It only reproduces when spawn ordering shifts, so you'd see it rarely and on someone else's machine.
- **A deleted listener still compiles.** With `Map<GameplayTagID, Array<callback>>`, nothing says who reacts to a stun. If you delete the HUD's subscriber, the build passes and the HUD silently stops updating. With a returned value, `perfect-typescripter/unconsumed-outcome` fails the build when a caller drops the outcome.
- **Re-entrancy.** `ClaimGameplayTag` calls the release path while it is still running, because a blocker arriving ends what it blocks. Granting fire immunity while burning would fire "burning removed" listeners in the middle of the immunity grant. A listener could then grant another tag and recurse into a half-updated table.
- **The granter's knowledge is thrown away.** Whoever removed the tag knew what should happen next, and a subscription makes them announce it and hope someone registered.

The lint rule `nro-codestyle/ban-a-list-of-callers-to-tell-later` refuses the subscription shape for these reasons. That means a `Connect`-style list on the tag container wouldn't pass lint anyway.

**What the wiring costs.** One owner performs the mutation and tells its collaborators, and the HUD is a constructor parameter on that owner. Adding a reader is one parameter in one place, and adding an applier touches no reader. The ADR says this grows the same way a subscription does, with the wiring type-checked and no startup window. It also admits the cost: the owner's constructor list grows with the game. When that list gets hard to read, the ADR treats it as a signal to name "everything that reacts to this change" as its own thing.

The ADR exempts Roblox's own signals, because the engine gives you no call to make. A message system is also allowed later, as long as the caller passes it the returned change on a visible line, like `messages.Send(taken)`.

**What decides it:** whether a missed reaction can be caught at compile time. A returned value that must be consumed can be, and a registration that never happened can't.
