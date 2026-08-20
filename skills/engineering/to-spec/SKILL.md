---
name: to-spec
description: "Turn the current conversation and repository understanding into a user-facing feature spec without starting a new interview. Use after alignment when the behavior, scope, and decisions need one durable specification."
short_description: "Turn aligned decisions into a feature spec."
disable-model-invocation: true
openai:
  interface:
    default_prompt: "Use $to-spec to turn our aligned decisions into a feature spec."
    brand_color: "#2563EB"
  policy:
    products:
      - "codex"
catalog:
  stage: "spec"
  order: 2
  aliases:
    - "write a feature spec"
    - "turn this into a spec"
    - "synthesize the spec"
  predecessors:
    - "grill-with-docs"
  when: "Alignment is settled and the work needs a durable, implementation-ready behavior contract."
  where_it_fits: "Second in the workflow chain. It turns the alignment brief into a spec for `$to-tickets`."
  success_signals:
    - "The spec states the problem, solution, user stories, decisions, testing decisions, and out-of-scope work."
    - "The spec names public seams and observable behavior without pretending implementation details are settled."
---

# Turn alignment into a spec

<what-to-do>

1. Read the current conversation, `CONTEXT.md`, relevant ADRs, and the repository surface touched by the request.
2. Synthesize what is already known. Do not restart the alignment interview. Flag a real contradiction instead of silently choosing between incompatible decisions.
3. Name the highest useful test seams. Prefer existing public boundaries and keep the number of new seams small.
4. Write the spec with these sections: Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope, and Further Notes.
5. Keep user stories extensive enough to cover success, failure, empty, permission, and recovery behavior. Keep file paths and code snippets out unless a prototype captured a decision that prose cannot express.
6. Publish to the configured tracker only when that integration exists. Otherwise write the spec artifact locally and say that publication is still pending.
7. End with the ticket handoff to `$to-tickets` and list the decisions that the ticket breakdown must preserve.

</what-to-do>

<supporting-info>

This is synthesis, not another interview. A spec is useful when another person can split it into independently verifiable slices without rediscovering the product decisions.

</supporting-info>
