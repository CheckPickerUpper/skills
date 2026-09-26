---
name: dependency-trace
description: "Dependency trace: clarify scope, close the recursive capability graph, and derive the correctness order before implementation. Use when the user asks what a feature uses, what its dependencies use, dependency order, foundations, or a lowest-to-highest flow."
short_description: "Clarify scope and derive the full dependency graph."
allow_implicit_invocation: true
---

# Dependency trace

Dependency trace is the leading word for finding the complete correctness road
from foundational contracts to higher behavior.

<what-to-do>
Enter dependency-trace mode when the user asks for dependency order,
foundations, the correct road, a lowest-to-highest flow, what a feature uses,
or what its dependencies use. Run the scope gate before searching the
repository or naming an issue.
</what-to-do>

<supporting-info>
Ordinary planning asks what can be built first. Dependency trace first closes
the complete capability surface, then asks what must exist for that surface to
be correct. Those are different orders.
</supporting-info>

## Procedure

<what-to-do>
### 1. Clarify and lock scope

Read the preceding conversation before choosing the target. Preserve the
user's quantifiers and constraints. “Every,” “all,” “full,” “complete,”
“proper,” and “system-wide” establish capability-complete scope. A request for
“what next” inherits the established scope; it does not narrow it to the
nearest issue or first runnable path.

When the conversation leaves the scope open and the choice would change the
graph, ask one focused clarification before tracing. Use the host's native
question tool when available; otherwise ask in prose:

```text
Should this dependency trace cover:

A. the complete capability surface, including everything it uses and
   everything those dependencies use; or
B. one bounded vertical slice, such as one input-to-runtime path?

I recommend A when the goal is to make the capability generally possible.
```

If the conversation already answers the question, state the locked scope and
continue without asking a redundant question.

Completion criterion: the output records the user's goal, locked scope, and
the evidence or answer that resolved any scope ambiguity before repository
exploration begins.
</what-to-do>

<supporting-info>
The skill failed when “make every ability possible” became “make one key press
activate one ability.” Scope is a graph boundary, not a descriptive preface.
</supporting-info>

<what-to-do>
### 2. Freeze the objective inside that scope

Begin with this header:

```text
Mode: dependency trace
Scope: {capability-complete or bounded slice}
Goal: {user's requested outcome}
Target surface: {the complete capability surface in that scope}
Invariant: {what must never be false when it is complete}
Deliverable: {dependency graph and topological order}
Work state: analysis only
```

Completion criterion: the target surface is broad enough to match the locked
scope, and no issue, task, or implementation path has been selected as the
target by itself.
</what-to-do>

<supporting-info>
The original request supplies the goal and destination. It does not decide
which prerequisite is foundational, and an issue number cannot define the
capability surface.
</supporting-info>

<what-to-do>
### 3. Close the capability graph before ordering it

Start at the complete target surface and inventory every concept it declares,
reads, writes, owns, produces, consumes, executes, or uses transitively. Check
all applicable surfaces before ordering anything:

- declaration and authoring;
- inputs and activation;
- ownership, grants, and lending;
- effects and outcomes;
- tags, attributes, formulas, conditions, facts, and world conditions;
- costs and cooldowns;
- lifecycle, removal, spawning, persistence, and networking;
- verification, content, and tests.

For every discovered concept, recursively expand its direct uses with this
edge:

```text
A ──uses──▶ B means A directly relies on B.
```

Trace downward to discover the graph; present the finished build order upward.
Do not stop at the first input, runtime, or user-visible path.

Completion criterion: every applicable surface is marked found, intentionally
not applicable, unresolved, or missing; every found concept has its direct
uses expanded; and no discovered concept is silently omitted.
</what-to-do>

<what-to-do>
### 4. Prove ownership and evidence

For every node, record its domain owner, design source, type or schema,
producer, consumer, implementation, open issue, or capability gap when the
repository provides one. Use `unknown after checking` when evidence is absent;
leave the branch unresolved instead of filling it with a guess.

An issue number, existing implementation, empty catalog, or “ready” label
proves identity or current state only. It does not prove that the node is a
dependency or that the current path is correct.

Completion criterion: every node in the capability graph has evidence, an
explicit unknown, or a documented reason it is not applicable.
</what-to-do>

<what-to-do>
### 5. Draw both dependency diagrams

Show the graph before showing the numbered order. Always include both:

1. **Usage diagram:** the complete semantic closure, with `uses` arrows from
   the requested capability to everything it requires transitively.
2. **Build diagram:** the correctness order, with `before` arrows from the
   foundational leaves to higher functionality.

Use labeled nodes and edge labels. If the graph is wide, split it into
branch diagrams that share the same root; do not replace a branch with prose.

Use this orientation for the build diagram:

```text
A ──before──▶ B means B cannot be correct without A.
```

For every edge in either diagram, write the corresponding proof:

```text
A uses B because {specific semantic requirement}.
B must follow A because {specific correctness or acceptance consequence}.
```

Completion criterion: both diagrams contain every graph node, every edge is
labeled with its direction, and every edge has a proof or is shown as
unresolved.
</what-to-do>

<what-to-do>
### 6. Classify nodes and derive the build order

Label each node as one of:

- **Design contract** — the domain meaning or invariant that must be settled.
- **Shared shape** — the type, data ownership, or boundary that carries it.
- **Lower functionality** — the first behavior that makes the contract real.
- **Higher functionality** — behavior composed from lower functionality.

Resolve a shared design contract before functionality that assumes it.
Reverse the proven usage dependencies into `before` edges, then topologically
order the result from:

```text
leaf design contract → shared shape → lower functionality → higher functionality
```

Independent branches may sit beside one another. Do not force a sequence
between nodes that have no edge.

Completion criterion: each node has one classification and owner where known,
and the order contains every graph node exactly once with no reversed edge.
</what-to-do>

<what-to-do>
### 7. Expose false foundations and incidental sequencing

Create separate sections for:

- **False foundations:** paths that compile, demo, or already exist but leave
  an invalid domain state reachable.
- **Not dependencies:** work that may be convenient to do earlier but is not
  required for correctness.
- **Unresolved:** facts or design decisions that prevent a proven edge.

Treat issue IDs as annotations added after the conceptual graph is complete.
They must not generate the graph.

Completion criterion: every proposed shortcut is either proved as a real edge,
listed as incidental sequencing, or rejected as a false foundation.
</what-to-do>

<what-to-do>
### 8. Stop at the analysis boundary

Report the scope, coverage, both diagrams, edge proofs, build order, false
foundations, incidental sequencing, and unresolved branches. A dependency
trace ends at analysis. If implementation is explicitly requested in the same
instruction, report the completed trace first and keep implementation as a
separate phase.

Completion criterion: the final line states whether analysis is complete and
whether implementation started.
</what-to-do>

## Ordering guardrails

<what-to-do>
Use correctness as the ordering criterion. Preserve capability-complete scope
when that is what the user requested. Cost, existing wiring, issue size,
shortest path, first playable result, MVP, and fastest implementation do not
break ties unless the user explicitly requests that optimization.

Call a semantic edge a dependency only when the upstream concept is actually
used. Call a build edge a dependency only when its absence makes a downstream
result incorrect or prevents its acceptance criteria. “It makes later work
easier” is not enough.
</what-to-do>

<supporting-info>
“Lowest leaf” means a node with no unresolved prerequisite. It means neither
the smallest issue nor the cheapest code change. A route that can demonstrate
the feature while permitting a forbidden state is not an available route.
</supporting-info>

## Output shape

<what-to-do>
Use this shape:

~~~md
## Dependency trace

Mode: dependency trace
Scope: capability-complete or bounded slice
Goal: ...
Target surface: ...
Invariant: ...
Work state: analysis only

### Scope decision

- ...

### Usage dependency diagram

```text
┌──────────────┐    uses    ┌──────────────┐
│ A            │───────────▶│ B            │
└──────────────┘            └──────────────┘
```

### Coverage ledger

| Surface | Direct uses expanded | Owner/evidence | Status |
|---|---|---|---|
| ... | ... | ... | found / not applicable / unresolved / gap |

### Build dependency diagram

```text
┌──────────────────┐  before  ┌────────────────────┐
│ foundational leaf│─────────▶│ higher functionality│
└──────────────────┘          └────────────────────┘
```

### Edge proofs

- A ──uses──▶ B — A uses B because ...
- A ──before──▶ B — B must follow A because ...

### Correctness order

1. ...
2. ...

### False foundations

- ...

### Not dependencies

- ...

### Unresolved

- ...

Analysis complete. Implementation started: no.
~~~

Completion criterion: a reader can verify the locked scope, complete coverage,
both diagrams, every edge, the leaf-to-higher order, and the stopping boundary
without reconstructing the agent's reasoning.
</what-to-do>

## Example

<supporting-info>
For a capability-complete ability trace, the usage diagram must expand beyond
the key path:

```text
┌──────────────┐    uses    ┌────────────────┐
│ Ability      │───────────▶│ GameplayEffect │
└──────┬───────┘            └───────┬────────┘
       │ uses                        │ uses
       ▼                             ├────────▶ Tags / Attributes / Formulas
┌──────────────┐                     ├────────▶ Conditions / Facts
│ Grant /      │                     └────────▶ WorldConditions
│ Lender/Input │
└──────────────┘
```

The build diagram is a separate view:

```text
┌──────────────────────┐  before  ┌──────────────┐
│ Facts / WorldConditions│───────▶│ Conditions   │
└──────────────────────┘          └──────┬───────┘
                                         │ before
┌──────────────────────┐                 ▼
│ Tags / Attributes    │────────────▶ GameplayEffects
└──────────────────────┘                 │ before
                                         ▼
                                   Ability execution
```

A global list assigned to every fighter may make a demo run, but it is a false
foundation if the invariant says a fighter can use only abilities lent to
them. The diagrams must show that false foundation separately rather than
letting it define the target.
</supporting-info>
