---
name: concrete-why
description: "Explain a decision so the reader can judge it without trusting you or opening an editor. Use whenever the user asks why, why not, what the rationale or benefit is, or pushes back on a recommendation. Answer the side that was asked; start from what the code or system does, never a verdict; describe every bug as a numbered sequence of real events; translate sources instead of relaying their phrasing; cut truisms; show the real code with added line-by-line comments; introduce every issue, file, or type with what it is, where it sits, and who uses it; say what you could not verify; and admit an empty side, flipping the recommendation when nothing concrete is left."
---

# /concrete-why

Explain a decision so the reader can check it without trusting you and without opening an editor.

## The failure this prevents

An explanation fails when the reader has to take your word for it or go read the code anyway:

> "NRO hands back the removal on purpose, and subscribing would cost more than it saves. Claim calls the release path while it is still running, because a blocker arriving ends what it blocks. The return value and the HUD subscription solve different problems."

The first sentence is a verdict. The second is the source's own phrasing relayed untranslated; nobody understands it without reading the code. The third is true of any two things. None of it says what happens.

## The rules

### 1. Answer the side that was asked

Restate the question to yourself in decision form first.

- "Why X?" asks what X gains.
- "Why not X?" asks what X **costs** or breaks.
- "What's the benefit?" asks for the gain, then whether it beats the cost.

"Why not move them" answered with "the benefit of moving is small" answers a different question.

### 2. Start from what happens, never from a verdict

Do not open with a ruling ("on purpose", "costs more than it saves", "the right call", "by design"). Open with what the code, system, or process actually does today, and let the reasons follow from it.

### 3. A bug is a numbered sequence of real events

A symptom ("the bar never greys out") is not an explanation. Write the failure as numbered steps: what runs, in what order, using the real names (tags, functions, frames, requests), and what the user or player sees at the end. Say when it happens and when it doesn't ("only when spawn setup runs before the HUD").

### 4. Translate sources; never relay their phrasing

An ADR, comment, or doc is evidence, not an explanation. If a sentence would only make sense after reading the code it describes, rewrite it as the steps it stands for. Quote a source only to show where a fact comes from.

### 5. Cut truisms and labels

Delete any sentence that would be true of any two options ("they solve different problems", "each has trade-offs"). These words never stand alone as a reason; use one only after the consequence it summarises:

stale · live · old · cleaner · simpler · consistent · best practice · idiomatic · robust · no real gain · not worth it · for tracking · proper · defining · canonical · risky · overkill · just cosmetic · on purpose · by design

### 6. A consequence keeps the size the facts give it

State each consequence as an observable difference: who or what sees it, where, when. When you project one forward, say what it rests on and write "can", not "will". Never upgrade a fact into a worse one: a "checkout incident" is not "customers unable to pay", and "most migrations" is not "39 of 41".

### 7. Introduce everything the argument rests on

The first time an issue, PR, file, type, function, incident, or rule appears, give:

- **What it is**: a linked title for issues and PRs; one clause for code ("the server code that sends each player their health and stamina bars").
- **Where it sits now**: its path, parent issue, milestone, status, or owner, when that bears on the decision.
- **Who uses it or waits on it**: the callers, lane, session, or person that depend on it. Check this; it often changes the answer ("only tests read this return value").
- **How much it matters**, when that changes the recommendation: priority, deadline, what breaks while it is open.

A bare `#1187`, a bare path, or a bare identifier makes the reader trust you. Do not write one.

### 8. Show the code the argument rests on

When a reason depends on code, show it. The reader is often away from their editor.

- Quote the real lines with `file:line`, keeping the code's own comments exactly as they are.
- Between the lines, add comments that say what each part does in plain language, marked `// ▸` so they are never mistaken for the code's own comments.
- When comparing two shapes, show both: before and after, or option A and option B.
- Trim unrelated lines with `// ...`. Show only what the argument needs.

```ts
// GameplayTagContainer.ts:231, inside ApplyGameplayTag
appliedTag.Applications.push(application);
// ▸ FireImmune is on from this line.

this.removeTagsBlockedBy(tag, application.Since);
// ▸ Takes off every Burning grant, one at a time.
```

### 9. Verify, and say what you could not

Every fact comes from something you read in this session. Check what can be checked before answering: grep for callers, read the function, confirm the rule is actually configured. If you infer, say "I infer" and from what. If something could not be confirmed, say so in its own line ("ADR 0003 says a lint rule enforces this; I could not find it configured"). Never add detail to an incident or timeline that the source does not contain.

### 10. Admit an empty side, and flip if it is empty

If an earlier answer leaned on a label or a convention ("same as the other routes", "cleaner"), quote it and say it was not a reason, even if the recommendation survives. If one option has no concrete consequence left after these rules, say so plainly and change the recommendation:

> "I have no concrete reason not to. My earlier recommendation was a default, not an argument. Move them."

When the items in the question do not all come out the same way, split them and say what separates the groups.

## Output shape

<what-to-do>
1. **Short answer**: what happens and what to do, in one or two sentences. No verdict words. If the recommendation changed, say so here.
2. **One block per item or option**, each opening with its introduction (rule 7), then the code (rule 8) and the consequences under each option (rules 3 and 6). Group items whose reasoning is identical.
3. **What I couldn't confirm**, when anything is unverified.
4. **What decides it**: one line naming the fact that separates the options, true for every item above, so the reader can apply it next time.
</what-to-do>

There is no length budget. Cut repetition, truisms, and sections for options nobody is weighing; keep every line that carries a fact. Do not end with a menu of follow-ups. The reply is prose, lists, and code; never copy this skill's tags or section names into it.

## Example

Question: "in NRO why does RemoveGrantedTag hand back a GrantedTagRemoval instead of just letting the hud subscribe to tag changes like unreal does with OnGameplayTagAdded? why not just subscribe its way less wiring"

> The HUD doesn't get tag updates from that return value at all; it checks a change counter. Subscribing would add two specific failures, shown below with the code.
>
> **How the HUD learns about tags today**
>
> `ParticipantResourceBarsPublisher` (`src/Shared/Server/Participant/ParticipantResourceBars.Server.ts`) is the server code that sends each player their health, stamina and chakra bars and their party panel. Nothing tells it a tag changed. After effects run, it compares a number:
>
> ```ts
> // ParticipantResourceBars.Server.ts:71
> const tagVersion = this.tags.ReadTagVersion();
> // ▸ Total number of tag changes on this player so far.
> if (tagVersion > this.publishedTagVersion) {
> // ▸ Bigger than at the last send means something changed since.
> 	this.publishedTagVersion = tagVersion;
> 	this.partyActions.PublishParticipant(this.player);
> 	// ▸ Resends the player's state to the party panel.
> }
> ```
>
> When the publisher is created it sends the current bars at once and records the counter, so a tag added before it existed is already in what it sent.
>
> **What `RemoveGrantedTag` returns, and who reads it**
>
> `RemoveGrantedTag` (`GameplayTagContainer.ts:266`) takes off one grant: one cause's hold on a tag, such as one of two enemies' `Burning`. It returns `GrantedTagRemoval` (`AppliedTag.Types.ts:212`): `Removed` with what is left of the tag, or `NotActive` when the grant was already gone. All 8 calls that read this return value are in `src/_Testing_/_Tests_/`; no game code reads it.
>
> **What subscribing would break** (reasoning recorded in `docs/adr/0003-a-mutation-returns-its-change.md`; `AGENTS.md` only says listener lists are banned)
>
> *1. The HUD misses a stun at spawn.*
> 1. A player spawns. On frame 1, spawn setup adds `Stunned`.
> 2. On frame 2, the HUD starts and registers "tell me when a tag is added".
> 3. "Stunned added" fired on frame 1, before anyone was listening.
> 4. The player is stunned, but their bars look normal for the whole stun.
>
> It happens only when spawn setup runs before the HUD. The counter cannot miss it, because the publisher sends current state when it starts.
>
> *2. A listener sees fire immunity and burning at once.*
>
> ```ts
> // GameplayTagContainer.ts:231, inside ApplyGameplayTag
> appliedTag.Applications.push(application);
> // ▸ FireImmune is on from this line.
> this.removeTagsBlockedBy(tag, application.Since);
> // ▸ Takes off each Burning grant, one at a time, through RemoveGrantedTag.
> // ...
> this.tagVersion += 1;
> // ▸ The counter the HUD checks goes up only after every removal is done.
> ```
>
> 1. The player is burning from two enemies, then gets `FireImmune`.
> 2. Enemy A's `Burning` grant comes off; "Burning removed" listeners run.
> 3. A listener asks "is the player burning?" and gets **yes**, because enemy B's grant is still on. The HUD keeps the burn icon on an immune player.
> 4. Enemy B's grant comes off and the listeners run again.
>
> **"Way less wiring"**: a listener needs a listener list on the tag container, a connect call in the HUD, and a disconnect when the player leaves. Today the publisher is handed `Tags` in its constructor (`ParticipantResourceBars.Server.ts:30`) and reads one number.
>
> **What I couldn't confirm:** ADR 0003 says `perfect-typescripter/unconsumed-outcome` makes ignoring a returned change a build error. I could not find that rule configured in the repo, and `removeTagsBlockedBy` itself ignores the return value, so today ignoring it compiles.
>
> **What decides it:** can the reader miss a change that happened before it started looking? A counter cannot; a listener can.
