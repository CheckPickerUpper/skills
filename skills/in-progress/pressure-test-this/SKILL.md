---
name: pressure-test-this
description: "Adversarial stress-test of an architecture, technical proposal, API contract, state machine, or plan before implementation. Clamps the target into six orthogonal stress vises: state explosion, temporal/interruption breakdown, adversarial intent evasion, cascading failure attribution, asymmetric load, and multi-owner drift. Prohibits severity theater: every fracture must demonstrate a concrete breaking execution trace and survive an adversarial refutation pass or be destroyed. Outlaws verdict theater: outputs lead immediately with What to do and Brief reasoning, followed by a correct-by-construction before→after fix. Clean approval is an expected, first-class outcome."
short_description: "Adversarial stress-test of technical designs, plans, and contracts."
allow_implicit_invocation: true
---

# /pressure-test-this

Subject a technical design, architecture, RFC, state machine, API contract, or implementation plan to adversarial real-world stress before code is written.

<what-to-do>
Activate this skill when the user asks to "pressure test", "stress test", "poke holes in", "find the edge cases in", or evaluate the resilience of a proposal, architecture, plan, or contract.

Run the phases in order. Findings are provisional until they pass Phase 2. Every survivor must carry a structural hardening fix.
</what-to-do>

## Lineage & Core Philosophy

This skill fuses the adversarial refutation rigor of `antimatter-code-quality-review` with the upstream prevention discipline of `correct-by-construction` and `pizza1`.

- **Zero severity theater:** Speculative "what-ifs" and generic edge-case doom-mongering are prohibited. A fracture is reported only if you can demonstrate the exact sequence of events or inputs that breaks an invariant under real domain constraints. Everything else is destroyed before output.
- **Zero verdict theater:** No report-card badges (`BLOCKS IMPLEMENTATION`, `Score: 7/10`, `Fatal Cracks: 2`). The reader needs to know **what to do** and **why**, not an arbitrary grade.
- **Clean approval is a first-class outcome:** When a design withstands all vectors without structural cracks, approve it directly. Manufacturing flaws to look thorough is a failure of this skill.
- **Correctness over convention:** Never defend or critique a design by pointing to what the codebase already does, what is conventional, or what creates the least diff.

## The Six Stress Vises

<what-to-do>
Clamp the proposal into these six orthogonal stress vectors:

1. **Permutation & State Explosion (The Cartesian Vise)**
   - Examine the Cartesian product of all states, options, flags, and optional fields.
   - Can partial initialization, missing payloads, or unexpected orderings put the system into a state that is syntactically valid but semantically impossible?
   - *Smell:* Independent boolean flags or loose optional fields representing a single underlying lifecycle.

2. **Temporal & Interruption (The Pizza1 Commits Vise)**
   - Force execution to abort mid-flight: crash, kill -9, network timeout, dropped socket, concurrent double-invocation.
   - Does state lead the world? Does the system record success before side-effects complete, or leave orphaned records on partial failure?
   - *Smell:* Non-idempotent retries, sequential multi-step writes without atomic boundaries, race conditions under rapid repeat calls.

3. **Adversarial Evaded-Intent (The Circumvention Vise)**
   - How will a caller, client, automated agent, or operator bypass the intended rule?
   - If a caller satisfies the letter of the schema or type but violates the domain invariant, can they still write the bad state?
   - *Smell:* Validation at the boundary that leaves raw unconstrained primitives forgeable downstream; secondary manual lanes or escape hatches left open.

4. **Cascading Failure & Attribution (The Opacity Vise)**
   - When a downstream dependency fails, degrades, or returns malformed data, how does the failure propagate?
   - Does one dependency failure poison unrelated subsystems? Does the error report the root cause, or mask it behind an uninformative timeout or generic catch-all?
   - *Smell:* Broad catches, discarded error causes, identical error codes for distinct failure reasons.

5. **Asymmetric Load & Cost (The Growth Vise)**
   - Scale one collection, entity, or payload $100\times$ or $10,000\times$ while others remain at $1$.
   - Name what quantity grows, and on what path frequency it runs (startup, per-request, or per-frame). Does algorithmic cost or memory allocation grow faster than the data?
   - *Smell:* Scanning collections inside repeating loops, per-call allocation on hot paths, unbounded queues without backpressure.

6. **Drift & Dual-Ownership (The 1-Fact-2-Owners Vise)**
   - When the system evolves, where will two components disagree on a single truth?
   - Are there hand-maintained mirrors of generated output? Are status fields derived from display strings? Are two independent schemas required to update in lockstep?
   - *Smell:* Parallel enums, manual mapping adapters across internal modules, duplicate validation rules across client and server.
</what-to-do>

## Procedure

<what-to-do>
### Phase 0 — Pin the Target & Invariants
1. Identify the exact plan, proposal, contract, or architecture being tested.
2. Formulate the non-negotiable **Core Invariants**: what must *never* be false if this system is correct?
3. State the invariants explicitly before testing.

### Phase 1 — Multi-Vector Stress Execution (Provisional)
Apply all six stress vises to the proposal. Trace the execution path under each stress condition and note every point where an invariant can be breached.

### Phase 2 — The Refutation Gate (Annihilation)
Actively attempt to refute every provisional fracture. Default to rejection unless evidence compels survival. Destroy a fracture when:
- It cannot produce a concrete, step-by-step breaking trace under realistic constraints.
- An existing upstream type, boundary, or framework invariant already makes the trace impossible.
- It relies on speculative external disasters (e.g. arbitrary hardware bit flips) rather than structural weaknesses.
- It is a style preference or convention argument without a concrete invariant failure.

Survivors are real fractures. Everything else is destroyed without comment.

### Phase 3 — Structural Hardening
For every surviving fracture, prescribe the **correct-by-construction structural upgrade**:
- Model, don't validate: replace loose booleans/optionals with sum types (discriminated unions).
- Move state commit to after effects run: state must never lead the world.
- Make operations idempotent by construction using domain keys, not retry counters.
- Unify dual owners into a single source of truth; delete translators and manual mirrors.
- A proposed fix that is merely "add a retry", "log a warning", or "remember to check X" is rejected as a patch. Provide the shape change that eliminates the failure class.

### Phase 4 — Output Contract
Format the output strictly by the contract below. Lead with **What to do** and **Why**.
</what-to-do>

## Output Contract

<what-to-do>
Never output scorecards, letter grades, or meta-status tables. Follow this shape:

### When Fractures Are Found:

#### **What to do:**
[One or two imperative sentences stating the exact structural change to make before implementation. Do not start coding until this is resolved.]

#### **Why:**
[Brief reasoning naming the core invariant that breaks under stress and what goes wrong if left unchanged.]

#### **💥 [Action That Sets It Off] → [Concrete Broken Result]**

**How it breaks:**
[One or two sentences explaining the failure mechanism in plain domain terms.]

**The breaking trace:**
1. [Step 1: specific input or state transition]
2. [Step 2: concurrent event, interruption, or edge condition]
3. [Step 3: the invariant breaches and observable failure occurs]

**The fix:**
- **Current plan:** [The fragile shape, sequence, or loose model]
- **Required shape:** [The correct-by-construction shape, atomic transition, or single-owner model that makes the failure unrepresentable]

*(Repeat the `💥` block for each surviving fracture. Separate blocks with blank lines).*

---

### When the Design Is Resilient:

#### **What to do:**
Proceed with implementation as planned.

#### **Why:**
[One concise paragraph naming why the design survived all six vectors: state transitions are atomic, invariants are enforced in the type shape, failure attribution is explicit, and no dual ownership exists.]
</what-to-do>

## Guardrails & Banned Output

<what-to-do>
- **No verdict theater:** Never output badges like `Verdict: BLOCKS`, `Grade: B+`, or `Score: 6/10`.
- **No empty coverage tables:** Never print a 6-row table listing vectors that were clean.
- **No patch compensations:** Never recommend a larger timeout, an extra retry, a caller checklist, or a warning comment where an atomic boundary or type shape is possible.
- **No pizza1 justifications:** Never defend a vulnerable shape because "it's what we usually do" or "it's the smallest change."
</what-to-do>
