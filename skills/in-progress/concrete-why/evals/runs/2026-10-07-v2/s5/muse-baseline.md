In NRO it's deliberate, not missing plumbing: [ADR 0003]( /home/ozzy-desktop/dev/NRO/docs/adr/0003-a-mutation-returns-its-change.md) bans Unreal-style `OnGameplayTagAdded` subscriptions.

`RemoveGrantedTag` in [GameplayTagContainer.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayTags/GameplayTagContainer.ts:266) mutates, then returns `GrantedTagRemoval` in [AppliedTag.Types.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayTags/AppliedTag.Types.ts:212) (`Removed + Presence` or `NotActive`). The caller that did the removal then tells the screen directly, in written order:

```ts
const ended = tags.RemoveGrantedTag(grant, at, reason);
screen.TagStandingChanged(ended); // no listener list
```

Why not subscribe:

* Startup race: HUD subscribing one frame after spawn setup grants `Stunned` never sees it.
* Silent deletion: removing a subscriber still compiles; dropping a returned outcome fails the build via `unconsumed-outcome`.
* Reentrancy: granting immunity removes `Burning` mid-grant; a listener firing inside that mutation can recurse into a half-updated table.
* Ownership: per [ADR 0008](/home/ozzy-desktop/dev/NRO/docs/adr/0008-a-cause-is-a-context-not-a-key.md), only the `GrantedTag` handle holder lifts that seat, so multi-grant stacking is safe. A tag-level broadcast can't say *whose* grant ended or what the standing now is.

The "less wiring" is inverted: one owner owns the mutation and gets collaborators constructor-injected (`TagGrants(tags, screen, analytics)`), so adding a reader is one constructor param. Subscription spreads that wiring across N dynamic registrations plus disconnect bookkeeping. Polling-style readers use `ReadTagVersion()` ([GameplayTagContainer.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayTags/GameplayTagContainer.ts:123)); event buses / listener lists are forbidden by the project's direct-fanout rule.
