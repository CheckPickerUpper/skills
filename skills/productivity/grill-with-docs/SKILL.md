---
name: grill-with-docs
description: "Align a fuzzy feature idea by asking only consequential questions, settling domain language, and recording decisions before a spec is written. Use when a design, product idea, or plan needs alignment."
short_description: "Align a fuzzy idea and record decisions."
disable-model-invocation: true
openai:
  interface:
    default_prompt: "Use $grill-with-docs to align this idea before we write its spec."
    icon_small: "./assets/icon-small.svg"
    icon_large: "./assets/icon-large.svg"
    brand_color: "#7C3AED"
  policy:
    products:
      - "codex"
catalog:
  stage: "alignment"
  order: 1
  aliases:
    - "align this idea"
    - "design interview"
    - "pressure-test the plan"
  when: "A fuzzy request has unresolved product, domain, ownership, or scope decisions."
  where_it_fits: "First in the workflow chain. It turns an idea into a shared vocabulary and a bounded destination for `$to-spec`."
  success_signals:
    - "Obvious decisions are inferred and only consequential forks reach the user."
    - "Settled terms, scope, and open questions are written down for the spec stage."
---

# Align before specifying

<what-to-do>

1. Read `CONTEXT.md`, nearby docs, and relevant ADRs before asking questions.
2. Restate the destination in the user's language. Separate the outcome from the proposed implementation.
3. Infer answers that are clear from the conversation, the repository, or basic product sense. Batch only questions whose answers change behavior, ownership, scope, or an irreversible decision.
4. For each real fork, state the recommendation and the consequence of choosing the other path. Ask for the decision in a small batch.
5. Record settled terms in `CONTEXT.md` when they are durable domain language. Record an ADR only when the choice is hard to reverse, surprising without context, and has a real trade-off.
6. Finish with an aligned brief: destination, settled vocabulary, decisions, unresolved questions, out of scope, and the handoff to `$to-spec`.

</what-to-do>

<supporting-info>

Alignment is complete when the next person can write a spec without reopening settled decisions. The conversation is the place for judgment; the repository is the place for durable language and decisions.

</supporting-info>
