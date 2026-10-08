It's a tag because Hora never runs any code while the flurry is held, so there is no place inside it to "check if stamina is 0." The project wrote this decision down in `docs/adr/0038-an-empty-resource-bar-is-a-gameplay-tag.md`.

**Why a check inside Hora doesn't work here**

- **The flurry is a wait, not a loop.** Hora is written as phases (`Hora.Ability.ts:122-138`). The flurry phase just waits for whichever comes first: you let go of the button, 1.5 seconds pass, or something else happens. Nothing in Hora runs each tick, so a check needs something to trigger it.
- **Hora doesn't spend the stamina.** The drain is a separate effect, `HoraStaminaDrain.GameplayEffect.ts`, that takes 2 stamina every 0.1 seconds. Hora only switches it on for the length of the phase, so it never sees the number change. Stamina could also hit zero from something outside Hora, like an enemy's drain or exhaustion.
- **So "just check" means one of two things, and the ADR rejects both:**
  1. **Polling:** check the bar every tick. This works out state indirectly instead of being told about it, which the project's "Take the dependency" rule forbids. It's also wrong between ticks: the bar can empty and refill between two checks, and the client and server can disagree about which tick saw zero.
  2. **A new "wait until this number hits zero" step for abilities:** that's a second way of watching things, used only by abilities. Ability gates, effect conditions and visual cues still couldn't see "empty", so each would need its own copy.

**What the tag gets you**

- **One owner, always consistent.** The code that changes a stat's number (the attribute container) adds or removes the tag in the same change that moves the number (`EmptyTag.ts:60-83`). The bar and the tag can never disagree.
- **Hora's side is one line.** `onTagAdded(Resources.Stamina.WhileEmpty.EmptyTag, strikeNearestForward)` uses the same "wait for a tag" step that combo attacks already use to cancel on stun (`M1String.ts:355`).
- **It works on the client too.** The container is shared code that runs on both machines, so the client predicts "empty" from the same change the server confirms.
- **Everything else can use it.** Every bar gets an empty tag: Health, Stamina, Chakra, Block, Awakening (`Resources.GameplayAttribute.ts:102-146`). A move that refuses to start at 0 chakra, or an "exhausted" visual, is an ordinary tag check.

**Where you're right:** today Hora is the only thing that waits on this tag. If it were the only consumer forever, the tag would be more machinery than it needs. The project's "Build the spine before the limbs" rule asks for the general form up front anyway. The cost is small: one tag per bar and a ~100-line `EmptyTag.ts`. Adding it later would mean going back and changing every place that had grown its own "is it empty" check.
