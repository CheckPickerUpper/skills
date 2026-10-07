**The return value and HUD subscription solve different problems.** `GrantedTagRemoval` tells the caller whether its particular grant was removed; a subscription would tell the HUD that something changed. Keeping the result does not itself require wiring every caller to the HUD.

In [GameplayTagContainer.ts](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayTags/GameplayTagContainer.ts:266), which owns a participant’s applied tags, removal returns:

- `Removed`, with the grant and resulting tag presence.
- `NotActive`, when that grant was already removed.

That distinction matters because **removing one stun grant does not necessarily end stun**: another grant can still hold it. Removing a suppression can also make the underlying tag present again. The HUD needs the resulting presence, not merely “a removal happened.”

The decision against subscriptions comes from [ADR 0003, “A Mutation Returns Its Change”](/home/ozzy-desktop/dev/NRO/docs/adr/0003-a-mutation-returns-its-change.md), which prescribes mutation followed by explicit calls to readers. It names two concrete problems:

- **Missed initialization:** if stun is applied before the HUD subscribes, the HUD misses the event. Reading current presence when attaching addresses that.
- **Callbacks during mutations:** applying immunity can remove burning inside the same operation. Immediately invoking a listener that changes tags can start another mutation before the first finishes. Delivering notifications after the operation completes addresses that.

Explicit calls make delivery order visible and dependencies required. Subscriptions reduce producer wiring, but require initialization and connection cleanup.

**Your wiring objection is fair, and the current code does not fully deliver the ADR’s proposed alternative.** The ADR requires one mutation owner to notify readers, but several callers—including effect and ability code—call `RemoveGrantedTag` directly and discard its result. Returning a value alone does not ensure the HUD updates.

What decides it is whether notification delivery is complete and happens after mutations finish. For HUD observation, I have no concrete reason to reject subscriptions that handle those conditions. NRO currently forbids them by architectural policy; `GrantedTagRemoval` is useful independently of that policy.