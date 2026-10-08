Abilities in NRO declare what events they wait for and go to sleep; they do not run code every frame to check numbers. Making "empty" a tag gives a held ability an event it can wait for, avoiding an every-tick polling loop.

**How abilities wait for things today**

`Hora` (`src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts`) is the silver rapier's flurry ability, used by fighters equipped with one. During its flurry hold phase, it does not run any logic on a loop. It hands the engine a list of events it cares about and stops executing until one happens:

```ts
// src/Shared/ReplicatedStorage/Content/GameplayAbilities/Hora.Ability.ts:130
			Continuation: {
				Kind: "Await",
				Race: firstOf(
					onInputReleased(strikeNearestForward),
					after(HORA_MAX_HOLD_DURATION, strikeNearestForward),
					onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward),
					// ▸ Wakes up and strikes the exact moment the tag goes on.
				),
			},
```

**How the tag gets applied**

`StateResourceEmptyStamina` (`src/Shared/ReplicatedStorage/Content/GameplayTags/State.GameplayTag.ts:211`) is the binary tag for stamina running out, read by abilities that drain it (accessed in code via `Resources.Stamina.WhileEmpty.EmptyTag`). The participant's attribute container puts this tag on in the exact same change that moves the stamina number to its floor, and takes it off the moment it rises.

```ts
// src/Shared/ReplicatedStorage/Content/GameplayTags/State.GameplayTag.ts:187
 * Each bar declares one of these as its Empty Tag, and the participant's attribute container puts it on the
 * moment the bar reaches its lower limit and takes it off the moment the bar rises...
 * A held ability that drains a bar races against it to end early when the bar runs dry.
```

**What checking stamina inside Hora would cost**

If running out of stamina was not a tag, there would be no `onTagAdded` event for `Hora` to listen to. The ability phase graph DSL (`src/Shared/ReplicatedStorage/GameplayDeclarations/PhaseGraph.ts`) provides event listeners for inputs, timers, and tags (`onInputReleased`, `after`, `onTagAdded`); it does not provide an `onAttributeZero` event or a primitive to poll numbers.

1. The player holds Hora; the ability enters the flurry phase.
2. The ability needs to know when stamina reaches 0, but no event fires from the number changing.
3. To find out, the ability would have to wake up 20 times a second (the game's simulation tick rate) to read the stamina amount.
4. The engine would spend CPU cycles repeatedly checking a number that has not reached 0, instead of letting the ability sleep until the exact moment it runs dry.

**What decides it:** A phase graph sleeps until an event wakes it; a tag provides that event, while checking a number requires polling.
