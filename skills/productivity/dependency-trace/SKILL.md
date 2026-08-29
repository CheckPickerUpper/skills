---
name: dependency-trace
description: "Dependency trace: derive the correctness graph before implementation. Use when the user asks for dependency order, foundations, or a lowest-to-highest flow for a feature, especially when they ask for the correct road before implementation or reject MVP/fastest-path planning."
short_description: "Derive the correctness order before implementation."
allow_implicit_invocation: true
---

# Dependency trace

Dependency trace is the leading word for finding the correct road from
foundational contracts to higher behavior.

<what-to-do>
Enter dependency-trace mode when the user asks for dependency order,
foundations, the correct road, a lowest-to-highest flow, or what must exist
before a feature. Treat the requested feature as the destination of the
analysis. Do not let the original feature request pull the work into
implementation before the trace is complete.
</what-to-do>

<supporting-info>
Ordinary planning asks what can be built first. Dependency trace asks what
must exist for the result to be correct. Those are different orders.
</supporting-info>

## Procedure

<what-to-do>
### 1. Freeze the objective

Begin with this header:

```text
Mode: dependency trace
Target: {behavior being worked toward}
Invariant: {what must never be false when it is complete}
Deliverable: {dependency graph and topological order}
Work state: analysis only
```

Completion criterion: the target, invariant, deliverable, and work state are
written before any task or issue is ranked.
</what-to-do>

<supporting-info>
The original feature request supplies the destination. It does not decide
which prerequisite is foundational, and it does not authorize a fastest-path
implementation.
</supporting-info>

<what-to-do>
### 2. Trace from the destination to the leaves

Start at the target behavior and list every fact, ownership relation,
boundary, and shared contract it requires. For each requirement, follow the
actual producer, writer, reader, caller, schema, or design document downward
until reaching a leaf with no unresolved prerequisite.

Trace downward to discover the graph; present the finished order upward.

Completion criterion: every requirement of the target reaches an evidenced
leaf, or is explicitly listed as unresolved.
</what-to-do>

<what-to-do>
### 3. Prove every edge

Use this orientation:

```text
A → B means B cannot be correct without A.
```

For every edge, write:

```text
B depends on A because {specific correctness or acceptance consequence}.
```

Use repository evidence when the edge depends on existing code or documents.
An issue number, existing implementation, or “ready” label is evidence of
identity only; it is not evidence of dependency.

Completion criterion: every edge has a reason that names the bad state or
missing behavior caused by omitting its prerequisite.
</what-to-do>

<what-to-do>
### 4. Classify the nodes

Label each node as one of:

- **Design contract** — the domain meaning or invariant that must be settled.
- **Shared shape** — the type, data ownership, or boundary that carries it.
- **Lower functionality** — the first behavior that makes the contract real.
- **Higher functionality** — behavior composed from lower functionality.

Resolve a shared design contract before functionality that assumes it.

Completion criterion: each node has one classification and its owner is named
when the repository proves one.
</what-to-do>

<what-to-do>
### 5. Produce the correctness order

Topologically order the graph from:

```text
leaf design contract → shared shape → lower functionality → higher functionality
```

Independent branches may sit beside one another. Do not force a sequence
between nodes that have no edge.

Completion criterion: the order contains every graph node exactly once, and
every dependency points from an earlier node to a later node.
</what-to-do>

<what-to-do>
### 6. Expose false foundations and incidental sequencing

Create separate sections for:

- **False foundations:** paths that compile, demo, or already exist but leave
  an invalid domain state reachable.
- **Not dependencies:** work that may be convenient to do earlier but is not
  required for correctness.
- **Unresolved:** facts or design decisions that prevent a proven edge.

Treat issue IDs as labels attached after the graph is correct. They must not
generate the graph.

Completion criterion: every proposed shortcut is either proved as a real edge,
listed as incidental sequencing, or rejected as a false foundation.
</what-to-do>

<what-to-do>
### 7. Stop at the analysis boundary

Report the trace and stop. A dependency trace does not create issues, edit
code, commit, or announce readiness to build. If implementation is explicitly
requested in the same instruction, report the completed trace first and keep
implementation as a separate phase.

Completion criterion: the final line states whether analysis is complete and
whether implementation started.
</what-to-do>

## Ordering guardrails

<what-to-do>
Use correctness as the ordering criterion. Cost, existing wiring, issue size,
shortest path, first playable result, MVP, and fastest implementation do not
break ties unless the user explicitly requests that optimization.

Call a change a dependency only when its absence makes a downstream result
incorrect or prevents its acceptance criteria. “It makes later work easier”
is not enough.
</what-to-do>

<supporting-info>
“Lowest leaf” means a node with no unresolved prerequisite. It means neither
the smallest issue nor the cheapest code change. A route that can demonstrate
the feature while permitting a forbidden state is not an available route.
</supporting-info>

## Output shape

<what-to-do>
Use this shape:

```md
## Dependency trace

Mode: dependency trace
Target: ...
Invariant: ...
Work state: analysis only

### Dependency edges

- A → B — B depends on A because ...

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
```

Completion criterion: a reader can verify the invariant, every edge, the
leaf-to-higher order, and the stopping boundary without reconstructing the
agent’s reasoning.
</what-to-do>

## Example

<supporting-info>
For an ability system, a global list assigned to every fighter may make a
demo run, but it is a false foundation if the invariant says a fighter can
use only abilities lent to them. A lender/cause contract can therefore be a
true prerequisite for a grant, the grant for granted-only runtime creation,
and the runtime for the first authored ability. World-condition access belongs
in the shared condition contract when an ability must be usable only under a
world condition; it is not a later polish item.
</supporting-info>
