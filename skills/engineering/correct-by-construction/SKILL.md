---
name: correct-by-construction
description: "Make a bad state impossible to write, at the earliest owner that knows it, with one owner per fact. Use for bugs, corrupted or generated artifacts, recurring agent mistakes, code smells, root-cause requests, 'prevent this class', bad APIs, models and schemas, repeated API or CLI friction, and enforcement rules (hooks, lints, guards, skills). Use when writing or reviewing types: deriving one type from another, loosening fields with optional, Partial, Any, Option or casts, or asking how to extract part of a type. Use for drift questions: 'where can this drift', 'is any fact owned twice', a check that said green while the enforcer said red, or before trusting a status surface. Locates the writer, strips incident words, names the class, climbs to the earliest owner (type, source of truth, generator, judge), removes competing representations and every bypass, and proves the bad state cannot be written."
metadata:
  when: "a whole kind of bug should be impossible, a type loosens or carves its source, or a fact may have two owners"
  situation: Something is broken
---

# /correct-by-construction

A bug is a state the design lets someone write. The fix is not a check beside
it; it is a design in which the state cannot be written at all, owned by the
earliest place that knows the rule, with every other route to the state
removed. One fact has one owner; every other copy is derived from it or
deleted.

"By construction" means the next caller receives a valid value, contract or
route without relying on memory, a final defensive check or a workaround. For a
class of invalid states, a type composition is the construction fix. A runtime
writer, parser, validator, clamp, evaluator or brand-minting function is
evidence or a residual boundary, never the type-level enforcer or the closure
proof.

The same standard covers two targets: a **bad state** that can be written or
constructed, and **evaded behavior** that gets around a rule through another
wording, token, route, wrapper or surface. Find the writer of the state or the
mechanism that enables the behavior, then close the whole class.

## Type-first default

<what-to-do>
"Class" is a routing signal, not a phrase the user must say. If the request
names a family of invalid states, variants, combinations or cases, begin with
the target language's types. Use sum types, product types, generic indices,
literal types, tuples and closed public surfaces so the bad composition fails
static checking before considering runtime code.
</what-to-do>

<supporting-info>
Accept language limits as part of the contract. If the type system cannot
express a numeric sign, range, unit conversion or arithmetic, say that property
is outside static closure. A brand, `unique symbol`, `as`, `any`, cast, or a
factory that checks a value does not change that limit.
</supporting-info>

## Operating stance

- **Failure is evidence.** A crash, timeout, empty result, rejected payload,
  race or failing check shows a design promise and the real system disagree.
  The observed error, reader, importer, screen or consumer is a witness, not
  the writer.
- **Follow the causal chain** before changing code:
  `writer → transformations and boundaries → invalid state → observed failure`.
  A fix written before the chain is known is a guess.
- **Correct the promise.** Find the false one (unbounded cost treated as
  bounded, raw value as valid, state as ready, rule as enforced, one fact as
  two classifications) and change the owner so it is true or cannot be made.
- **Keep validity separate from control flow.** Stop, retry, cancel, time out,
  catch, buffer and fall back are control-flow choices. Words such as "hang",
  "timeout", "silent" or "retry" describe the route, not the class. Use them
  only when bounded progress or recovery is itself the domain requirement; a
  timeout or catch that hides the bad state is a mitigation.
- **Replace padding with ownership.** When code says "just in case", find the
  writer that makes the case possible. Keep a defensive boundary only at a real
  external or hostile boundary whose input cannot be removed at the source.

## Derive before asking

<what-to-do>
Before asking the user anything, consult the governing standard, the project's
stated rules and the code, and record which you read. If any settles the
question, there is no question; implement the settled answer.

- Every option you present passes every rule. An option that leaves the bad
  state writable is eliminated, not offered.
- Never ask for a fact whose only use is narrowing the general form: how many
  callers, regions or providers exist today. The owner carries the whole
  domain; each caller declares its own value.
- **If the answer would change what the system supports rather than what a
  caller declares, the question is wrong.**
- A claim that nothing reads, writes or uses something covers every place a
  consumer can live: this repository, any repository its docs name as the
  owner, generated code and deployment configuration. Search all of them
  before calling it dead or asking the user.
</what-to-do>

## Protocol

Run these steps in order. Diagnosis and prevention are one answer.

### 1. Lock scope and authority

Preserve the request's quantifiers: "every", "all" and "the whole class" need
class-wide coverage. Decide whether edits are authorized. Read-only means no
edits, never no prescription.

Done when the scope, target and edit authority are stated and the work has not
narrowed itself to the first visible symptom.

### 2. Locate the writer or enabling mechanism

> **Do I know who or what wrote the bad state?** If not, keep tracing.

Read the code, artifact, transcript, configuration, generator, hook or
workflow that proves how the state or behavior is created: who writes,
constructs, persists, generates, copies or mutates it; who chooses the route;
which transformations change it; which boundary reports or compensates for it.
A reader, parser, importer, crash site or failing consumer is evidence about
the result. When a reader rejects a malformed file, trace what wrote,
truncated, templated or copied the file; when a screen hides a button, trace
who persisted or dropped the state.

Done when one concrete writer is named with the path, symbol, artifact or
transcript line that proves it.

### 3. Name the concrete bad state

State the smallest real value, relationship, artifact, transition or route the
design permits, not a smell category: "`status` is `error` while
`errorMessage` is null", not "the state can be inconsistent". Keep the
incident's exact value in the evidence, not in the class name.

### 4. Strip incident vocabulary

Remove the words inherited from the witnessed case: proper names, feature,
file and function names, commands, screens, framework terms, local lifecycle
words, values and timings. Then run the swap test:

> If the incident nouns are replaced with a sibling case, does the stripped
> sentence still describe the failure?

Add a word back only when it defines every member of the class. Good: "a
capped value can be stored above its maximum." Bad: "this job increments this
counter after this limit record is missing."

### 5. State the rule positively

Write the rule the system guarantees by construction: callers receive a domain
value, not a raw shape; one owner exposes one classification per fact; a
generated artifact has one source; an operation's cost is represented
honestly; an enforcement surface blocks the intent while valid boundary cases
stay available. The rule never depends on a caller remembering a checklist.

### 6. Climb to the earliest enforcing place

Test every candidate owner with both questions:

1. **Swap:** with a sibling case, can the same stripped bad state still happen?
2. **Before it runs:** can source, configuration, generated output, a public
   API call or a raw data shape still spell it directly?

Either yes means the candidate is too low. Prefer the earliest place that knows
enough, in this order:

1. a closed type algebra or public type surface;
2. a compiler or type checker that rejects the artifact;
3. the source of truth whose types define the output;
4. a schema or generator that emits the type;
5. a domain type, state machine or metric-indexed API;
6. a closed generic or literal-type registry;
7. a private constructor plus one parser, or a module boundary that prevents
   the old type from being named;
8. the runtime writer, only after proving no earlier owner can carry the rule.

A **judge** is whatever refuses an artifact before a human must notice: a
compiler, type checker, linter, schema validator, owning generator, or a test
or CI job that runs on every change. A checklist is not a judge. Unrepresentable
beats refused: once the class has been witnessed more than once, a judge
outranks any lower manual fix, because recurrence proves site fixes are not
holding, but never outranks a type or source of truth that removes the state.
When no judge covers a recurring class, that gap is the finding.

**An existing owner is evidence, not closure.** Answer all four:

1. What owner is supposed to control the fact?
2. Which writer, caller, manual lane, adapter or fallback bypasses it?
3. What exact change removes, redirects, seals or makes that bypass uncallable?
4. What proof shows the next consumer cannot meet the bad state?

Without an answer to 3, the bug can still happen; say so.

**When the owner is a judge, run it; do not read it.** Run it against the
artifact that carries the bug and paste the result. Prove: its mechanism can
express the property (a linter cannot see a type invariant, a type checker
cannot see whether a write was readable, a schema cannot see a cross-file
relationship); its matcher matches this shape, not only the shape it was
written for; it reaches the artifact by language, path and selection; and it
runs where the artifact is authored. For a judge that does not exist yet, show
it refusing the pre-fix artifact before prescribing it. A judge that allows
the file containing the bug is a second finding.

Runtime enforcement is valid only after the raw bad shape is gone: a
constructor may clamp, normalize or reject using runtime facts, but callers
receive a domain value they cannot fake with a plain number, string, map entry
or loose record.

Done when one earliest owner is named, both tests pass, and any judge has a
demonstrated refusal.

### 7. Give each fact one owner

Before accepting a mapping, switch, lookup table, normalizer, adapter or
paired classification, ask:

> Do the two sides answer different domain questions, or are they competing
> spellings of one fact?

Signals of competing spellings: identity cases pass through while others are
renamed or collapsed; collapsed cases differ only by scope or a value that
could live inside one case; the target exists so a consumer can recover a
category the source should expose; a hand-written type maintained beside a
runtime schema of the same data. Keep both only when each has an independent
meaning or belongs to an external contract this owner cannot replace, a source
distinction changes behavior outside the projection, and one side is derived
at the boundary rather than stored as a second authority. Otherwise put the
fact in one classification, move real variation into payload or a nested
closed type, have consumers read the owner, and delete the translator.
Deriving from the one source (`type Order = Static<typeof orderSchema>`) is
correct; two that must agree is the defect. Exhaustiveness proves coverage,
not single ownership.

### 8. Remove representations with no independent job

For every alias, projection, label, status, wrapper, carved subset or
reconstructed contract, inspect at least one place above the boundary that
actually knows the value.

> If consumers received the authoritative value, state or transition directly,
> would this representation still have a job?

If not, carry the owner's value with its branch-specific evidence and delete
the representation. A representation that cannot drift can still be
unnecessary. "Best within the current design" is not owner proof when changing
the design deletes it. Do not wait to be asked whether going higher changes
the answer.

### 9. Reject compensations that leave the route open

Name the route each lower fix leaves open. Patch signals: a local null check,
clamp, broad catch, default or fallback; a larger timeout, retry or buffer; a
token-only regex; a doc warning, comment or reviewer checklist; a binding
remap, adapter, compatibility or legacy lane; a second classification kept in
sync by a conversion. Keep one only with an independent domain purpose and the
bad state already impossible upstream.

### 10. State the required change exactly

Name the surface, symbol or path that must change; what it must own or accept;
every writer, lane, adapter, fallback or escape to remove, redirect, seal or
make uncallable; and the observable result that proves the next consumer no
longer compensates. "Use the existing owner" is not a change.

### 11. Make the owner protective

When editing is authorized, change the enforcing place so future callers
receive the protected state by construction: the public contract, type
algebra, schema, generator, generic constraint or closed registry. No local
runtime patch, shim or call-site fix while the old type is still available.
When editing is not authorized, return the same prescription and mark closure
unproved.

### 12. Delete every bypass lane

Sweep direct constructors and raw literals, manual copies beside generated
output, alternate APIs and wrappers, fallback branches, configuration and
fixtures that spell the raw form, rules that cover one token or path, and
consumer surfaces still exposing the old contract. Redirect or remove each.
No expert mode, legacy lane or lower-level escape survives that can recreate
the state.

### 13. Prove the class is closed

- the smallest former bad composition fails the type checker, build,
  generator or constructor, without a cast or `any`;
- the sibling valid composition is accepted;
- the judge refuses the pre-fix witness, when one is involved;
- when editing is authorized, a test at the owner fails on the pre-fix code
  and passes after;
- a sweep finds no old symbol, raw shape, mapping or lane;
- any property the language cannot express is named as an unclosed residual,
  not disguised as a brand or runtime check.

Report the verification command, its exit code and the evidence that the old
writer is gone. Only after this proof, look for sibling classes (references
below).

## Route by shape

Load the matching reference and fold its result into the one answer. Load more
than one when the bad state spans them. Do not hand the user a menu of these.

| Load | When the bad state is |
| --- | --- |
| [`references/data-shape.md`](references/data-shape.md) | a local data shape or a type that carves or loosens its source: a struct, union, enum, field cluster, outcome type, optional field, `Pick`/`Omit`, cast |
| [`references/public-surface.md`](references/public-surface.md) | a public surface that lets callers assemble an invalid design or sequence: an API, CLI, test runner, macro set, generator, workflow, or several public lanes for one intent |
| [`references/unit-cohesion.md`](references/unit-cohesion.md) | a boundary between units of delivery: one whole split by aspect, independent wholes fused under one name, or a shared capability placed under its first caller |
| [`references/enforcement.md`](references/enforcement.md) | the work product is enforcement (a hook, lint, guard, schema rule, skill or agent-behavior rule), or a guard fired and someone wants to weaken it |
| [`references/one-fact-sweep.md`](references/one-fact-sweep.md) | a sweep rather than one located bad state: where can facts drift, which facts have two owners, where can construction replace checks across a target |
| [`references/similar-classes.md`](references/similar-classes.md) | the original class is closed and the user asks where else the same shape can happen |

## Never

- Stop at the component that noticed the bad state, or prescribe prevention
  before the writer is located.
- Classify into a named smell instead of the concrete bad state, or let the
  incident's vocabulary donate the abstraction.
- Call "the writer enforces it every time" prevention while callers can still
  spell the bad state as raw data.
- Accept a runtime owner without proving the rule cannot live in the type,
  schema, generator, constructor, parser, registry or public surface.
- Treat an exhaustive mapping, switch, table or adapter as closure before
  proving its two sides are different facts.
- Keep a derived alias, label or wrapper because it cannot drift, when a higher
  owner can delete it.
- Say "the correct owner already exists" as the answer, or describe a bypass as
  history without prescribing its removal.
- Add a guard, fallback, retry, lint, comment or doc and call it prevention
  while the old write path exists; keep the old lane beside the corrected one.
- List patch-versus-root options when one option leaves the bad state writable.
- Call a check, judge or mechanism real and stop there. A real need still
  needs an owner for its code: before keeping custom code, check existing
  code, the platform, a maintained library or a service, in that order.
  Changed-file selection, time limits and generating migrations from a schema
  are standard capabilities. Never say no library does it without the search
  that shows it.
- Give a verdict that rests on an unchecked "if". Check whether the owner
  change is possible now, and state the result.
- Rest a verdict on remembered upstream behavior. When one documentation tool
  is unavailable, read the official site, and leave the outage out of the
  answer.
- Name a higher owner by intuition after being challenged, without the
  stripped sentence and a swap-test proof.
- Call the nearest shared helper the owner when a higher source of truth owns
  the rule.
- Use a brand, cast, parser, clamp or evaluator as type construction, or claim
  static closure for a property the language cannot express.
- Run a similar-class sweep before the original class has its before-it-runs
  proof, or use one to avoid reopening a leaked path in the original class.

## Output shape

<what-to-do>
Show the answer formatted, never inside a code block. Open with one bold
sentence that answers the question. Then give every distinct class its own
block, with a blank line between blocks:

- A bold numbered label that names what happens, in the reader's words.
- Then these bullets, in this order, each one line, or sub-bullets with one
  change or one check each:
  - **Now:** what happens today, with the decisive measurement or value.
  - **Where:** the writer that creates the bad state, not what notices it, as
    a path and symbol.
  - **Class:** the sentence from step 4.
  - **Fix:** the earliest owner and each structural change, one per
    sub-bullet, with every bypass removed.
  - **Can't come back:** the type, judge, generator or check that refuses the
    bad state from now on.
  - **Proof:** one check per sub-bullet. When code changed, the verification
    command, its exit code, and the evidence the old writer is gone. When the
    class is still open, what remains open and the missing proof.

End with **What needs you:** what only the user decides or does, or that
nothing does.

Write each bullet as one fact in the field's standard terms. Add a small code
shape only when it makes the bad or fixed shape clearer. No preamble, no
paragraphs under a label, and no closing summary that repeats the blocks.
</what-to-do>

<supporting-info>
Example:

**Replays send notifications twice, and server code builds client pieces.**

**1. Replays send duplicate notifications**
- **Now:** replaying an order's history sends its "shipped" notification again
  on every replay.
- **Where:** the rebuild emits through the public notifier, keyed by a newly
  allocated handle.
- **Class:** internal reconstruction can publish external events under
  temporary identities.
- **Fix:**
  - Replay side effects stay private to the rebuild.
  - Published events are keyed by the order's stable id.
- **Can't come back:** the notifier accepts only a stable-id key type.
- **Proof:** a repeated-replay test sees one notification.

**2. Server construction needs client presentation**
- **Now:** server code passes no-op presentation stand-ins to build a player.
- **Where:** the server aggregate's constructor requires presentation adapters.
- **Class:** an authoritative server aggregate depends on client-only
  presentation services.
- **Fix:**
  - Split shared presence from server behavior and client presentation.
  - Remove presentation from the server constructor and delete the stand-ins.
- **Can't come back:** the server package has no import of the presentation
  package, and a check refuses one.
- **Proof:** the server compiles against its own interface.

**What needs you:** nothing.
</supporting-info>
