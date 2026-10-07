---
name: concrete-why
description: "Explain a decision so the reader can judge it without trusting you. Use when the user asks why, why not, what the rationale or benefit is, or pushes back on a recommendation — and always when they ask about the same point a second time, because that means the first explanation failed. Every reason names an observable consequence, never a label; every issue, PR, file, or component the argument rests on is introduced with what it is and how much it matters; and a side with no concrete consequence left is admitted, flipping the recommendation if needed."
---

# /concrete-why

Explain a decision so the reader can check it without trusting you.

## The failure this prevents

An explanation fails when it restates the conclusion in other words:

> "Moving them changes only how they're displayed. It also means editing old planning issues for no real gain. Leave all seven where they are."

Nothing in that reply tells the reader what goes wrong if they do the opposite. "No real gain", "old", "live work item", "defining spec" are labels. They describe the speaker's verdict, not the world. The reader is left to trust the verdict or ask again.

## The rules

### 1. Answer the side that was asked

Restate the question to yourself in decision form before answering.

- "Why X?" asks for what X gains.
- "Why not X?" asks for what X **costs** or breaks.
- "What's the benefit?" asks for the gain, then whether it beats the cost.

Answering "why not move them" with "the benefit of moving is small" answers a different question. Name what goes wrong if they are moved, or say nothing does.

### 2. A reason is an observable consequence

Each reason says **who or what sees a difference, where, and when**: a progress bar that drops an item, a session that no longer finds the bug, a build that takes 40 seconds longer, a user who loses a save.

These words never stand alone as a reason. Use one only after stating the consequence it summarises:

stale · live · old · cleaner · simpler · consistent · best practice · idiomatic · no real gain · not worth it · for tracking · proper · defining · canonical · risky · overkill · just cosmetic

### 3. Introduce everything the argument rests on

The reader should be able to judge the reasoning without opening a link or remembering a number.

- An issue or PR appears as a link with its title, then one line saying what it is.
- When the argument depends on how much the thing matters, say so concretely: what breaks or stays blocked while it is open, its priority or deadline, who is waiting on it.
- A file, component, or setting gets one clause saying what it does.

A bare `#1187` or `the old parent` forces the reader to trust you. Do not write one.

### 4. Check every reason before sending

- **So-what test.** Ask "so what?" of each reason once. If the answer is the conclusion again, the reason is circular. Cut it.
- **Both-sides test.** If the reason would hold whichever option is chosen, it does not separate them. Cut it.
- **Source test.** Each fact comes from something you read in this session (a command output, a file, an issue body). If you are inferring, say "I infer" and from what, and do not give an inferred number more precision than its inputs. If you have not checked something checkable, check it before answering. Do not add detail to an incident or a timeline that the source does not contain.

### 5. Admit an empty side, and flip if it is empty

If one option has no concrete consequence left after step 4, say so in plain words:

> "I have no concrete reason not to. My earlier recommendation was a default, not an argument. Move them."

Defending an earlier recommendation is never a reason. When the analysis contradicts what you said before, lead with the change. When the earlier answer leaned on a label or a convention ("same as the other routes", "cleaner"), quote it and say it was not a reason, even if the recommendation survives.

When the items in the question do not all come out the same way, split them and say what separates the groups.

## Output shape

<what-to-do>
1. **Short answer**: one or two sentences with the recommendation. If it changed from before, say so here.
2. **One block per item or option.** For each:
   - what it is (linked title, one line, how much it matters)
   - where it stands now, if that matters
   - *If we do X:* the concrete consequences
   - *If we don't:* the concrete consequences
3. **What decides it**: one line naming the fact that separates the options, so the reader can apply it themselves next time. It must give the right answer for every item above; if no single fact does, name one per group or leave the line out.
</what-to-do>

Keep it as short as the decision allows:

- Group items whose reasoning is identical ("#402 and #404 both shipped through PRs that never linked them") instead of repeating a block.
- Write both *If we do* and *If we don't* only when both sides have a consequence worth stating. For three or more items with the same shape, a table (item, what it is, what each option does) is shorter.
- Do not add sections for options nobody is weighing. Do not end with a menu of follow-ups.

## Example

Question: "Why NOT move #318 and #254 under their lane issues so everything is in one place?"

> **Short answer:** No reason not to. Move them. I recommended leaving them earlier out of a default against touching old issues, not because of a cost.
>
> **[#254 Save slot overwritten on rapid exit](https://github.com/owner/repo/issues/254)**: high-priority data-loss bug; a player who quits twice within a second loses their save. It blocks lane 7. It sits under [#88 Q2 persistence planning](https://github.com/owner/repo/issues/88), a planning issue closed in June.
> - *If moved under [#1272 Lane 7: persistence](https://github.com/owner/repo/issues/1272):* it appears in the sub-issue list and progress bar the lane 7 session works from, so the session sees it without reading the brief.
> - *What moving costs:* it leaves the sub-issue list of a closed issue nobody opens. Nobody loses anything.
>
> **[#1187 Inventory desyncs after reconnect](https://github.com/owner/repo/issues/1187)**: medium-priority; items duplicate until the next sync. Its parent is [#1150 Reconnect protocol rewrite](https://github.com/owner/repo/issues/1150), the issue lane 3 is actively working from.
> - *What moving costs:* an issue has one parent. Moving it drops it from #1150's progress bar, and lane 3 would read reconnect as finished while this bug is open.
>
> **What decides it:** whether anyone tracks work from the current parent.
