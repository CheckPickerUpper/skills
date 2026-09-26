---
name: correct-by-construction
description: "Make classes of invalid states and evaded constraints unreachable by type composition first. Use for bugs, bad APIs, models, schemas, generated artifacts, and enforcement rules. Treat the target language's type system as the enforcer, accept its limits, and never substitute runtime checks, brands, casts, or workarounds for a type-level construction."
---

# /correct-by-construction

For any prompt that presents a class of invalid states, start at the type
algebra or public type surface. The type system is the enforcer: compose types
so valid states are inhabitable and the class's invalid combinations fail
before execution. Then trace the earliest supporting owner and prescribe or
implement the structural change that closes the whole class.

"By construction" means the next caller receives a valid value, contract, or
route without relying on memory, a final defensive check, or a special
workaround. For a class of invalid states, a type composition is the
construction fix. A runtime writer, parser, validator, clamp, evaluator, or
brand-minting function can be evidence or a residual boundary, never the
type-level enforcer or closure proof.

## Type-first default

<what-to-do>
"Class" is a routing signal, not a phrase the user must say. If the request
identifies a family of invalid states, variants, combinations, or semantic
cases, begin with the target language's types. Do not wait for "types only".
Use sum types, product types, generic indices, literal types, tuples, and
closed public surfaces to make the former bad composition fail static
checking before considering runtime code.
</what-to-do>

<supporting-info>
Accept language limits as part of the contract. If the target type system
cannot express arbitrary numeric sign, range, unit conversion, or arithmetic,
state that property is outside static closure. A brand, `unique symbol`,
`as`, `any`, cast, or constructor/factory that checks a value does not change
that limit. Runtime validators, clamps, parsers, runtime-only tags, and
evaluators can enforce behavior, but they are not type construction and do
not prove the class closed.
</supporting-info>

## Operating stance

### Treat failure as evidence

A crash, timeout, empty result, rejected payload, race, or failing check is
evidence that a design promise and the real system disagree. It is not an
obstacle to silence. Trace the promise back to the place that allowed the
contradiction.

The observed error, stack frame, reader, importer, screen, or consumer is a
witness. It is not automatically the writer or the owner.

### Follow the causal chain

Before changing code, be able to state:

```text
writer or enabling mechanism
  → transformations and boundaries
  → invalid state or evaded behavior
  → observed failure or workaround
```

If the chain is incomplete, continue tracing. A fix written before the chain
is understood is a guess.

### Correct the promise

Find the false promise: unbounded cost treated as bounded, raw value as valid,
state as ready, rule as enforced, or one fact as two classifications. Change
the owner so the promise is true by construction or cannot be made.

### Keep validity separate from control flow

Stopping, retrying, cancelling, timing out, catching, buffering, or falling
back can be valid control-flow requirements. They do not make an invalid state
valid. Use them only when bounded progress, recovery, or failure handling is
independently part of the domain. A timeout, retry, default, or catch that
only hides the bad state is a mitigation, not a class fix.

### Replace padding with ownership

When code says "just in case," locate the writer that makes the case possible.
Move the rule upstream, narrow the public input, or remove the route. Keep a
defensive boundary only when it protects a real external or hostile boundary
whose invalid input cannot be removed at the source.

## Two targets, one standard

<what-to-do>
Use this protocol for a **bad state** that can be written or constructed and
for **evaded behavior** that circumvents a rule through another wording, token,
route, wrapper, or surface. Find the writer for a state and the enabling
mechanism for behavior, then identify the whole class, move ownership upstream,
close every bypass, and prove closure.
</what-to-do>

## Data-shape lens

<what-to-do>
When related fields can be absent, inspect their **Cartesian product** before
adding guards. Use a **product type** for data that exists together in one
valid state and a **sum type** for mutually exclusive lifecycle states; put
state-specific fields inside their variant. Bundle fields that are created,
destroyed, or updated together. For a class of invalid states, **model, don't
validate**: make the invalid composition fail in the type shape itself. Design
a public API as a **pit of success**, where valid construction is natural and
invalid construction is unavailable. Do not turn this type-level rule into a
runtime parser, validator, or factory.
</what-to-do>

<supporting-info>
n independent binary fields permit 2^n combinations; the count is a signal
that the shape may admit invalid combinations, not proof by itself. Repeated
absence checks often show that one lifecycle is split across loose fields. A
boolean validator leaves the raw value forgeable and makes every caller wonder
whether validation happened.
</supporting-info>

## Protocol

Run these steps in order. Do not split diagnosis from prevention.

### 1. Lock scope and authority

Read the request and preserve its quantifiers. "Every," "all," "system-wide,"
and "the whole class" require class-wide coverage. Decide whether the task is
analysis-only or authorizes edits. A read-only request still requires an exact
prescription; it only changes whether you apply it.

Adding tests, fixtures, compile-fail cases, or new scenarios requires explicit
user authorization. If authorized code makes an existing test stale, update
that test; do not expand coverage by default.

Completion criterion: the scope, target, and edit authority are stated, and
the work has not narrowed itself to the first visible symptom or caller.

### 2. Locate the writer or enabling mechanism

Read the code, artifact, transcript, configuration, generator, hook, or
workflow that proves how the bad state or behavior is created. Trace:

- who writes, constructs, persists, generates, copies, or mutates the state;
- who chooses the route that permits the behavior;
- which transformations change its shape or meaning;
- which boundary reports, rejects, or compensates for it.

A reader, parser, importer, crash site, UI observer, or failing consumer gives
evidence about the result. It does not prove the cause.

Completion criterion: one concrete writer or enabling mechanism is named with
the source path, symbol, artifact, transcript line, or person-facing rule that
proves it.

### 3. Name the concrete bad state or circumvention

State the smallest real thing the current design permits: a value,
relationship, artifact, transition, route, or intent, not a smell category.
Name what can be written or reached, not what the user called it. Keep the
incident's exact value or token in the evidence, not in the class name.

Completion criterion: the concrete invalid state or circumvention can be
pointed to in the writer's output and is not merely a symptom label.

### 4. Strip incident vocabulary

List the words inherited from the witnessed case: proper names, feature names,
file names, commands, screens, framework terms, function names, local state
names, concrete values, and timing details. Remove them before naming the
class.

Then run the sibling test:

> If the incident nouns are replaced with a sibling case, does the same
> stripped sentence still describe the failure?

Add a word back only when it defines every valid member of the affected class.
The first observed feature, file, lifecycle name, or token is evidence, not an
abstraction.

Completion criterion: the class sentence remains true after the incident
vocabulary is removed and the nouns are swapped for a sibling case.

### 5. State the rule positively

Write the rule the system must guarantee by construction:

- callers receive a domain value instead of a raw shape that can be invalid;
- one owner exposes one classification for one domain fact;
- a generated artifact has one source of truth;
- an operation's cost or progress bound is represented honestly;
- an enforcement surface blocks the intent being circumvented, while keeping
  independently valid boundary cases available.

The rule must not depend on a caller remembering a checklist or on a reviewer
recognizing one spelling.

Completion criterion: the rule names the valid construction or route and the
invalid construction or route it removes.

### 6. Climb to the earliest enforcing place

Test every proposed owner with both questions:

1. **Swap:** after replacing the incident with a sibling case, can the same
   stripped bad state or behavior still happen?
2. **Before it runs:** can source code, configuration, generated output, a
   public API call, or a raw data shape still spell it directly?

If either answer is yes, the candidate is too low.

For a class of invalid states, prefer the earliest type-level place that
actually knows enough, in this order:

1. a closed type algebra or public type surface;
2. a compiler or type checker that rejects the artifact;
3. the source of truth whose types define the output;
4. a schema or generator that emits the type;
5. a metric-indexed API, domain type, or state machine;
6. a closed generic or literal-type registry;
7. a module visibility boundary that prevents the old type from being named.

The runtime writer is evidence about the failure, not the type-level owner.
If the language cannot express the property, report the static boundary
instead of moving the fix into a constructor, parser, validator, or evaluator.

"Judge" means a compiler, type checker, linter, schema validator, generator,
or required test/CI job that refuses the relevant artifact before a human must
notice. A checklist is not a judge.

An unrepresentable state is stronger than a refused state. When the class has
been witnessed more than once, an existing judge outranks a lower manual fix
because recurrence proves site fixes are not holding. That does not make the
judge stronger than a type or source of truth when those can remove the state
entirely.

When the proposed judge does not yet exist, prove all four properties before
prescribing it:

- **Expression:** its mechanism can decide the property;
- **Matching:** its rule matches this shape, not only the original example;
- **Reach:** its language, path, and selection include the artifact;
- **Execution:** it runs where the artifact is authored.

Then run it against the pre-fix artifact and show it refusing the exact bad
shape. A judge that returns allowed on the artifact containing the bug is a
finding, not proof of ownership.

Completion criterion: one earliest owner is named, the swap and before-it-runs
tests pass, and any proposed judge has a demonstrated refusal or a documented
reason a higher construction owner removes the need for it.

### 7. Give each fact one owner

Before accepting a mapping, switch, lookup table, normalizer, adapter, or
paired classification, ask:

> Do the two sides answer different domain questions, or are they competing
> spellings of one fact?

Keep both only when:

- each classification has an independent meaning or belongs to an external
  contract this owner cannot replace;
- a source distinction changes behavior outside the target projection, or the
  external contract requires that distinction;
- one side is derived at the boundary rather than stored beside the other as a
  second authority.

Otherwise, put the shared fact in one classification, move real variation into
payload or a nested closed type, update consumers to read the owner directly,
and delete the translator and parallel cases. Exhaustiveness proves coverage,
not single ownership.

Completion criterion: every surviving classification has a different question
to answer, and the source of truth plus every writable spelling is named.

### 8. Remove representations that have no independent job

For every alias, projection, label, status, wrapper, or reconstructed contract,
inspect at least one place above the proposed boundary that actually knows the
value, state, or transition.

Ask:

> If consumers received the authoritative value, state, or transition directly,
> would this representation still have an independent job?

If no, carry the authoritative value and its branch-specific evidence, then
delete the detached representation. If yes, name the different domain question
or independently controlled external boundary it serves, and derive it there
instead of storing it beside the owner.

Completion criterion: every surviving representation has a named independent
purpose, and at least one higher owner was checked before accepting it.

### 9. Reject compensations that leave the route open

For each proposed fix, name the route it leaves open. Treat these as patch
signals when they are being used to avoid changing the owner:

- a local null check, clamp, broad catch, default, or fallback;
- a larger timeout, retry, cancellation, or buffer;
- a token-only regex or example-specific behavior rule;
- a documentation warning, comment, reviewer checklist, or caller convention;
- a local binding remap, adapter, compatibility lane, or legacy escape hatch;
- a second classification kept synchronized by a conversion.

Keep one of these only when it has an independent domain purpose and the bad
state is already impossible upstream. Otherwise, reject it and name the
upstream writer it leaves available.

Completion criterion: every lower fix is either tied to an independent domain
requirement or rejected with the exact remaining bypass.

### 10. State the required change exactly

Turn the owner and bypass evidence into a prescription another person can
apply. Name:

- the file, symbol, contract, schema, generator, type, registry, hook, rule,
  or workflow that must change;
- what that surface must own or accept;
- every writer, caller, manual lane, adapter, fallback, or escape hatch to
  remove, redirect, seal, or make uncallable;
- the observable result that proves the next consumer no longer receives the
  bad state or repeats the workaround.

"Use the existing owner" is not a change. An existing owner is only evidence
until every bypass is closed.

Completion criterion: the prescription has an exact target, an ownership
change, a bypass deletion list, and an observable proof condition.

### 11. Make the owner protective

When editing is authorized, change the type-enforcing place so future callers
receive the protected state or route by construction. Change the public
contract, type algebra, schema, generator, generic constraint, or closed
registry that creates the possibility. Do not add a local runtime patch while
the old type remains available. A constructor, parser, validator, clamp, or
evaluator is not a type-level fix.

When editing is not authorized, return the same exact prescription without
pretending the class is fixed.

Completion criterion: the blessed owner itself prevents the class, rather than
merely checking a result after an old writer has produced it.

### 12. Delete every bypass lane

Sweep all writers and routes that can still create or select the class:

- direct constructors and raw object literals;
- manual copies beside generated output;
- alternate APIs, adapters, wrappers, and fallback branches;
- configuration and fixtures that spell the raw invalid form;
- hooks or rules that cover only one token or one path;
- generated or consumer surfaces that still expose the old contract.

Redirect callers to the protected owner or remove the route. Do not leave a
documented expert mode, compatibility lane, legacy lane, or lower-level escape
that can recreate the same state.

Completion criterion: the sweep identifies every old writer and each one is
removed, redirected, sealed, or proven to represent a different class.

### 13. Prove the class is closed

Run the proof at the owner and across the reachable surfaces:

- compile, build, generate, parse, or construct the smallest former bad form;
- run the required judge against the pre-fix witness when one exists;
- exercise the sibling case from the swap test;
- run the authorized owner-level test or update an existing stale test;
- sweep for old symbols, raw shapes, old mappings, and alternate lanes;
- when editing code, run the relevant verification command and report its exit
  code and the evidence that the old writer is gone.

The class is closed only when the former bad state or evaded behavior cannot be
written or reached through the type surface anywhere in scope. A passing
runtime test, runtime clamp, correct existing owner, or successful local
workaround is not type-level closure.

For a class of invalid states, the primary proof is static:

- the smallest former bad composition fails the target type checker without a
  cast or `any`;
- the sibling valid composition is accepted;
- every public type route and raw representation has been swept; and
- any property the language cannot express is named as an unclosed residual,
  not disguised as a brand or runtime check.

Completion criterion: the proof covers the owner, a sibling case, every
writer/route, and the before-runtime judge or construction boundary, with no
unresolved bypass.

## Enforcement branch: block the intent, not the token

When the work product is a hook, lint, guard, schema, type restriction, skill,
rulebook, or agent-behavior block, apply this branch inside the same protocol.

### Name the intent being evaded

Start with the behavior the caller or agent is trying to get away with, not the
token that appeared in the example.

| Observed door | Whole behavior to examine |
|---|---|
| `any`, an escape cast, or an ignore directive | making the type lie to avoid representing a real case |
| a phrase such as "out of scope" | deflecting a correctness issue with a non-correctness reason |
| one wrapper around a supervised loop | giving the lifeline the same failure fate as the work it supervises |
| a named screen, lifecycle, or feature-specific helper | making the first consumer own a capability shared by other consumers |

The table supplies examples, not a permanent token list. Search for alternate
spellings, routes, names, and mechanisms that serve the same intent.

### Run the letter check

Before shipping an enforcement rule, write:

```text
Incident words:              <tokens, names, or local mechanisms in the example>
Stripped rule:               <the rule after those words are removed>
Class-defining words added:  <word plus proof that the whole class needs it>
Remaining bypasses:          <open routes, or none at this layer>
```

If the rule blocks the observed token while the intent remains reachable,
expand the rule or state the exact lower layer that must own it. If the rule is
so broad that it blocks an honestly valid boundary case, narrow it to the
intent and require the boundary reason or domain type that distinguishes the
valid case.

### Preserve honest exceptions

Precision is part of correctness. A genuine external boundary may have a
runtime check, but that check is a residual boundary fact, not the type-level
class fix. An adapter may have a conversion for a contract it does not own.
Neither may replace the type composition that enforces the class, and neither
is closure proof when the target language cannot express the property.

Completion criterion: an alternate spelling or route cannot perform the same
wrong act, and an independently valid boundary case remains expressible with
its real contract or reason.

## Route by shape

Use the smallest applicable lens without creating a second doorway:

- **Class of invalid states:** start with the type algebra and make the bad
  composition unnameable or unassignable.
- **Public surface:** make valid construction natural and remove the route that
  can construct the invalid one.
- **Local data shape:** use a closed state representation; avoid parallel
  booleans, loose fields, and split lifecycles that permit impossible states.
- **Repeated instances:** move the shared construction rule to its owner and
  sweep every instance for the old shape.
- **Unit boundary:** keep one whole responsibility together; do not split one
  deliverable by aspect or fuse independent wholes under one name.
- **API or CLI friction:** close the missing capability in one blessed lane and
  remove wrappers or fallback APIs that preserve the gap.

Completion criterion: the selected lens changes the owner or construction
surface rather than adding a symptom check.

## Output shape

Lead with the change, then explain the failure, then show the proof. Write it
as a direct answer, not a diary of searches.

```text
The change:              exact file, symbol, surface, or contract and what it must own

What is failing now:     existing owner that is not enough and the route that bypasses it

The bad shape:           smallest concrete invalid value, relationship, or behavior

Why it lets the bug in:  how the current writer or surface permits it

The fixed shape:         protected type construction and the static proof
```

Then include only the proof lines that apply:

```text
Wrote it:                writer or enabling mechanism, with evidence
Bad state:               concrete invalid value or situation
Words stripped:          incident vocabulary removed before naming the class
The class:               stripped sentence that survives the sibling swap
Why possible:            structure that lets the writer create or reach it
Rule that must hold:     construction or route that must be valid
Who must enforce it:     earliest owner that can actually reject or remove it
Why that one:            coverage, timing, and ownership proof
Required change:         exact target and new responsibility
Other ways in to shut:   writers, lanes, adapters, fallbacks, or escapes
One fact, one owner:     competing spellings and the one deleted
Copies still needed:     surviving derived representations and their jobs
Same bug, different case: sibling swap and why the fix still holds
Caught before it runs:   compile, build, generation, construction, or judge proof
Smaller fixes rejected:  compensation and the bypass it leaves open
Fix:                     structural change that makes the owner protective
Deletes:                 old writers, manual lanes, mappings, and escapes
Proof:                   why no route can create or reach the class
Test:                    authorized owner-level test or the reason no seam exists
Swept for:               symbols, raw shapes, callers, and old lanes checked
```

For a read-only task, make no edits but still provide this prescription. For an
authorized code change, report the verification command, exit code, and direct
evidence that the former writer or bypass is gone.

## Closure failures

<what-to-do>
Treat the answer as a patch when it stops at the observer, names the incident
instead of the stripped class, leaves an existing owner's bypass open, accepts
raw invalid input after a runtime check, keeps competing facts or needless
representations, blocks one token while the intent has another door, or uses a
mitigation while the old writer remains available. It is also a patch when it
uses a brand, cast, parser, clamp, or evaluator as type construction, or claims
static closure for a property the language cannot express. Reopen the protocol
until a sibling swap, before-execution type proof, and complete type-route
sweep pass.
</what-to-do>
