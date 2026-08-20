---
name: grill-with-docs-requiem
description: A high-judgment design interview that sharpens plans in useful batches and records settled domain language and ADRs as the conversation progresses.
short_description: "Sharpen plans and record settled decisions."
disable-model-invocation: true
catalog:
  stage: "alignment"
  order: 80
  aliases:
    - "batch design questions"
    - "record settled decisions"
  when: "A plan needs a design interview that resolves real forks and records domain language."
  where_it_fits: "Use for a deeper alignment conversation when the decision record matters as much as the questions."
  success_signals:
    - "Only consequential questions reach the user."
    - "Settled terms and ADR-worthy decisions are recorded as the conversation moves."
---

# grill-with-docs-requiem

Run a Requiem interview: press the design hard enough to expose real decisions, but do not make the user pay for questions an expert can infer. Use `/domain-modeling` throughout. Do not inherit `/grilling`'s one-question-at-a-time cadence for this skill; this skill batches questions because it is also maintaining docs and domain language.

## Invalid Behavior

Do not outsource obvious judgment to the user. A question is invalid when the answer is already clear from the scene, the existing docs, the codebase, or basic product sense.

Invalid question patterns:

- Asking whether a selected character should duplicate in its original seat and the center spotlight when the user already said the character moves.
- Asking a naming question where one option is ambiguous and the other names the domain concept clearly.
- Asking one tiny fork at a time when the next five forks are independent and can be answered together.
- Asking for permission to create `CONTEXT.md` or an ADR after the skill rules already say when those files should be created.

## Operating Rule

Default to: "I lean toward X because Y. I am treating that as the working decision unless you correct it."

Ask only when the answer changes one of these:

- the domain model or ubiquitous language
- an ADR-worthy trade-off
- a player/user-facing behavior
- a data ownership boundary
- a risky implementation direction
- a scope boundary that would change what gets built

If the question would only confirm the obvious, infer the answer and keep moving.

## Question Tool Routing

When a real fork needs the user's answer, use the host's native question tool if one exists.

- Claude agents: use the `AskUserQuestion` tool.
- Any other agent with a native question or user-input tool: use that tool.
- If the tool supports multiple prompts, send the whole question batch in one call.
- If no native question tool exists, ask in prose using the batch shape below.

Do not use a question tool for inferred decisions. State the working decision and continue.

## Question Batches

Ask questions in sets of 3-7 when the answers can be considered independently. Keep each question short, but include the recommended answer and the reason it matters.

Use this shape:

```md
I am inferring these unless you correct me:

1. **{Decision name}**: I recommend {answer} because {reason}.
2. **{Decision name}**: I recommend {answer} because {reason}.

Real forks:

1. **{Decision name}**: I lean toward {answer} because {reason}. Is that the intended direction?
2. **{Decision name}**: I lean toward {answer} because {reason}. Is that the intended direction?
```

Do not ask more than 7 questions at once. If more forks exist, group them by theme and continue after the user answers the current batch.

## The Obviousness Gate

Before asking, run this check silently:

1. Can the codebase, existing docs, or user statement already answer it?
2. Is one answer clearly invalid, duplicative, impossible, or nonsense in the described product?
3. Would a competent product or domain designer infer the answer without bothering the user?
4. Would the answer fail to change docs, architecture, behavior, or scope?

If any answer is yes, do not ask. State the inference only if it helps the conversation or the docs.

## Domain Language

Names must be clear over terse. Do not suggest ambiguous ubiquitous-language terms just because they are shorter.

Good terms identify the thing at the level a future reader needs:

- **Saved Character Seat** is better than **Seat** when the concept is a persistent menu placement for a saved character.
- **Featured Mark** is better than **Center** when the concept is the presentation target for the selected character.
- **Featured Saved Character** is better than **Selected** when the concept is the saved character currently presented in the spotlight.

When proposing a glossary term:

- Name the concept, not the UI widget or implementation mechanism.
- Include `_Avoid_` terms for ambiguous alternatives.
- Reject names that could refer to multiple concepts in the same conversation.
- Prefer a longer precise term over a short term that future agents can misuse.

## Docs Cadence

Use the `/domain-modeling` skill's file rules and formats.

- Update `CONTEXT.md` immediately when a term is resolved.
- Create ADRs only for decisions that satisfy the ADR test: hard to reverse, surprising without context, and a real trade-off.
- Batch ADR questions by theme. Do not ask one ADR fork at a time unless one answer blocks every other question.
- Do not put implementation notes, animation timing, UI copy, or scratch decisions in `CONTEXT.md`.

## Final Check

Do not merely batch bad questions. Batching five obvious questions is still invalid.

Spend user attention only on decisions that need user judgment. Infer the rest, state the working decision when useful, and keep moving.
