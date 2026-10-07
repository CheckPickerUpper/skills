Short version: the return value and a subscription do different jobs, and NRO doesn't have to choose between them. `RemoveGrantedTag` returns a `GrantedTagRemoval` so the caller learns what its own call did. It isn't the HUD's way of finding out that a tag changed.

**What the return value is for** (`AppliedTag.Types.ts:205-214`, `GameplayTagContainer.ts:266-298`):
- The caller hands in the exact `GrantedTag` it holds, and the container removes that one application, found by object identity (`indexOf(grant.Application)`).
- The result is either `Removed` with the new `TagPresence`, or `NotActive / AlreadyRemoved`.
- `NotActive` means nothing happened. That covers a double release, or a tag that something else already took off, such as a cleanse, a death, a blocker arriving or an exclusion-group push.
- The caller needs that answer at the call site, right then. A broadcast about "tag X changed" can't say whether *this* call was the one that did it.
- The same holds for `TagApplicationResult` on apply, which returns `Blocked` or `Granted` with the grant. The repo's rule is to name results for the question, not the happy path.

**Why not use a subscription for that:**
- The repo forbids "Router classes, event buses, and dynamic listener lists", and wants lifecycle transitions fanned out "through direct method calls on concrete collaborators" (`CLAUDE.md`, "Direct transition fanout").
- The container already makes its own changes observable another way: `this.log.ApplicationTaken` and `this.log.ApplicationRemoved`, plus a monotonic `tagVersion`.
- The HUD can read the container directly with `ReadGameplayTagPresence` (the `ParticipantTags` interface). It can also compare `tagVersion` to know when to re-read.

**Your actual point has some force.** Unreal's `OnGameplayTagAdded` / `RegisterGameplayTagEvent` is a UI-facing notification, and the return value doesn't replace one. There is no subscribe-to-tag-changes surface in `GameplayTagContainer.ts`. A HUD that wants a change pushed to it has two options today: poll `tagVersion`, or have whoever applies or removes the tag call the HUD directly. That is the wiring cost you're describing. I haven't checked how the HUD currently reads tags, so I can't say how bad it is in practice.

If you want a subscription, it should be a separate surface, not a replacement for the return value. Under the repo's rules it would also have to be a concrete collaborator that the container calls directly on add and remove, not a generic listener list. That is a real design change, and it probably deserves an ADR.
