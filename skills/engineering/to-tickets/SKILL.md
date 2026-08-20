---
name: to-tickets
description: "Break a spec or aligned plan into tracer-bullet tickets with observable outcomes, explicit blockers, and a dependency order. Use after a spec when implementation needs independently verifiable vertical slices."
short_description: "Break a spec into vertical tickets."
disable-model-invocation: true
openai:
  interface:
    default_prompt: "Use $to-tickets to break this spec into vertical tickets with real blockers."
    brand_color: "#0891B2"
  dependencies:
    tools:
      - type: "mcp"
        value: "github"
        description: "Publish approved tickets and native blocking relationships when GitHub is configured."
        transport: "streamable_http"
  policy:
    products:
      - "codex"
catalog:
  stage: "tickets"
  order: 3
  aliases:
    - "break this into vertical tickets"
    - "tracer-bullet tickets"
    - "split the spec into tickets"
  predecessors:
    - "to-spec"
  when: "A spec exists and implementation needs small, complete slices that can be verified independently."
  where_it_fits: "Third in the workflow chain. It creates the dependency frontier for `$implement`."
  success_signals:
    - "Each ticket crosses the required layers and has a user-observable acceptance criterion."
    - "Every blocker is genuine, named, and ordered before the ticket it gates."
---

# Break the spec into tickets

<what-to-do>

1. Read the full spec and its decisions. Inspect the repository only where it changes the ticket shape.
2. Prefer tracer-bullet vertical slices that cross every required layer and are demoable or verifiable alone. Use an expand–migrate–contract sequence for a genuinely wide mechanical refactor.
3. Give every ticket a short outcome title, what it makes work, observable acceptance criteria, and a `Blocked by` list. Put blockers first in dependency order.
4. Present the proposed granularity and edges for approval when they materially affect scope. Do not ask about obvious splits.
5. Publish approved tickets to the configured tracker in dependency order. If no tracker is configured, write one local ticket file per slice and report the publication boundary.
6. Hand the first unblocked slice to `$implement`; do not close or rewrite a parent issue as part of ticket creation.

</what-to-do>

<supporting-info>

A ticket is a complete path through the product, not a layer-shaped task. The dependency graph exists to show what can start now and what must wait, not to turn ordinary sequencing into a blocker.

</supporting-info>
