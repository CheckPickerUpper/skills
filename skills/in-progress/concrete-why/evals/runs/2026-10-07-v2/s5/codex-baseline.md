Because NRO explicitly chose **returned outcomes and direct calls over subscriptions** in [ADR 0003](/home/ozzy-desktop/dev/NRO/docs/adr/0003-a-mutation-returns-its-change.md). The reasons are visible dependencies, explicit reaction order, avoiding missed startup notifications, and preventing callbacks from changing tags halfway through another mutation.

But **the return value and HUD notification solve different problems**.

[`RemoveGrantedTag`](/home/ozzy-desktop/dev/NRO/src/Shared/ReplicatedStorage/GameplayTags/GameplayTagContainer.ts:266) returns whether *that specific grant* was removed or was already inactive, plus the resulting tag presence. Removing one stun grant can leave Stunned active because another grant still holds it. That result is useful to the caller regardless of how the HUD receives updates. Returning it and emitting a notification could coexist.

And yes: **subscribing is less wiring for a HUD**. The risks the ADR names are manageable: read current presence when binding, own the connection’s lifetime, and deliver notifications after the mutation finishes. The ADR overstates matters when it says subscriptions cannot carry a change value or support logging—they can.

NRO’s intended alternative is one mutation owner that receives concrete collaborators and forwards changes. That avoids every tag producer knowing about every reader. **The implementation does not fully establish that arrangement:** several systems call the container directly and discard removal results. The returned value alone therefore does not guarantee the HUD gets updated.

So the honest answer is: this is an architectural policy choice, not a necessity imposed by gameplay tags. Your wiring objection is valid. Under NRO’s current rules, the answer is to centralize mutation and presentation delivery; adopting HUD subscriptions would mean revisiting that policy.