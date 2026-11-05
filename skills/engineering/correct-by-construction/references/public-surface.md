# Public surface: make the valid path the only path

Load this when the bad state lives in a public surface (an API, domain model,
type, module, schema, CLI, test runner, macro set, hook, generator or
workflow) that lets callers or agents assemble an invalid design or sequence
and depends on them to avoid it, or when repeated friction, local wrappers,
compatibility layers or several public lanes answer one consumer intent.

A **pit of success** is a public shape where the normal path leads to the
valid design and the invalid design is absent, private, unconstructable or
rejected by a mandatory mechanism. Instructions, warnings, runtime checks and
tests do not close a public construction path by themselves.

## The crime

**The public design makes invalid states or sequences writable and depends on
callers or agents to avoid them.** For a command or flag surface: it lets
callers combine implementation knobs into invalid attempts instead of
accepting one intent-shaped request that the system prepares, validates and
owns end to end. The flag, sibling command or documented "remember to clean up
first" step you saw is one door.

## Answer

The findings go into the main answer's blocks, one fact per bullet: say whether the surface is right, the surface
that should exist, and the check, shape or hard cut that makes the wrong path
unavailable; then the bad shape, why it makes callers do extra work, and the
fixed shape. No options menu, no compatibility compromise.

## Close the gap

Run in order, writing an answer to each:

1. **Name the friction** and the invalid design or attempt the surface permits.
2. **Who can create it:** every actor (a person reading docs, an agent reading
   `--help`, a script) and every public discovery path that reaches it.
3. **Sibling lanes:** every command, flag combination, macro, function or alias
   a caller would reach for to express the same intent. These compete.
4. **The smallest upstream invariant** that makes the invalid attempt
   impossible to express, not caught and rejected.
5. **One blessed surface,** named by the intent a normal user has, that
   prepares, validates and owns the whole sequence the caller now assembles by
   hand. Define it as a named type, constructor, API, schema or owned
   transition.
6. **Hard-cut the wrong lanes** (below) and propagate the new shape through
   every consumer and boundary.
7. **Add the enforcement** the remaining escape paths require (ladder below).
8. **The next-agent test:** next agent, next week, same situation, normal
   discovery path: do they hit this gap again? If yes, it is open; keep going.

Design the shape for the whole class first (what bad state is possible, who
can create it, where else the shape appears, what invariant makes it
impossible everywhere), then name the first implementation slice. Words such
as "if needed", "for now", "advanced", "manual", "escape hatch", "low-level",
"later" and "probably" in an answer about the correct shape mean the local
symptom is being optimized. A variant may be left out only when it is
explicitly unsupported, with the rule that rejects it.

## Shape rules

| Bad shape | Pit-of-success shape | Net |
| --- | --- | --- |
| `isLoading` and `hasError` can both be true | One state: loading, success or failure | 2 flags → 1 state; invalid combinations cannot be written |
| Any text can be passed as a user ID | One creation step accepts valid identity text | raw text → validated value; unvalidated text cannot enter |
| Public fields allow an incomplete payment | One creation operation returns an accepted payment or a named rejection | open fields → outcome; incomplete payments cannot circulate |
| The caller assembles setup, workers and cleanup | One operation owns the sequence | 4 caller steps → 1 operation; no step can be skipped or reordered |
| A runtime check guards a public bad constructor | The constructor is private and parsing owns creation | the bad value has no normal creation path |
| The caller hand-writes a lowered form and must keep it consistent with the source | The caller states intent; the lowered form is derived | the inconsistency has nowhere to be typed |

## Invalid-attempt smells in a command, flag or job surface

Each hit is resolved or explicitly cleared:

- **Mechanism flags on the normal run command:** a knob (`--engine`, `--mode`,
  `--transport`) the caller must set correctly. The system knows the right
  value; it sets it.
- **Contradictory options:** two flags that can be passed together but make an
  undefined run (`--watch --once`). Make the pair unrepresentable.
- **Hidden liveness preconditions:** the command works only if something else
  is already running, built or logged in, and nothing makes that visible. The
  caller learns by failure.
- **Cleanup rituals:** the happy path needs "clear the old run first". A
  repeated cleanup step is the friction restated.
- **Several commands for one intent:** `run` and `test` and `check`; `deploy`
  and `push` and `release`. One intent, one verb.
- **Diagnostics that can mutate or run:** a status or inspect command that can
  also change state is a second door into the run lane.

## Hard-cut rule

When a caller can choose between the correct-by-construction path and a path
that can assemble an invalid state, do not keep the invalid path as a
documented option, expert mode, escape hatch, compatibility, legacy or
lower-level lane. Remove the choice: make the wrong path private, sealed,
non-namable or generated-only; make direct use fail at compile or contract
time; migrate callers mechanically. Keep a callable path only when it answers a
genuinely different intent: name that intent and the invariant that prevents
overlap. A diagnostic stays only if it is read-only.

The rule covers procedures too. A step someone repeats every time the
situation recurs (re-toggle, re-delete, reconnect, "remember to X") is the gap
spelled out. A manual step is allowed only when it is one-time and the wrong
state can never form again afterwards.

Do not over-block: a rule that removes a flag or command answering a different,
read-only intent trains people to route around the surface.

## Enforcement ladder

Use the strongest available proof:

1. a type shape that makes invalid construction fail;
2. a private constructor or private expansion target;
3. a generated descriptor, schema or client;
4. a compile-fail case for the removed lane;
5. a runtime case for external or untyped input;
6. a hook or lint when the language cannot express the invariant;
7. a generator or installer check when consumers could receive stale surfaces.

If the normal path can still write the bad form, the pit is open.

## Rejected moves and stop reasons

- A local wrapper when an upstream library, generator, schema or plugin owns
  the invariant; a compatibility layer as the final design; several public
  macros or functions for one intent; docs that explain which of two callable
  APIs is right; a technical name where a plain domain name exists.
- A close that ends on a manual step the loop repeats.
- A claim about a live system you have not proved you can see. When a close
  depends on a daemon, session, deployed service or registered plugin, prove it
  is reachable first; if not, say you cannot see it and stop inferring.
- Origin or prevalence as a reason to stop: "pre-existing", "not mine", "out
  of scope", "the codebase already does this", "rare", "only on one platform".
  Only correctness or an external contract you do not own (semver, a
  third-party API) stops the close.

## Naming gate

Before accepting a public name: what exact intent does it answer; does another
public name answer the same intent; does it explain the choosing axis without
comments; would a non-specialist understand it; would someone searching by the
symptom find it first? Prefer plain words over protocol trivia: `sensitive
text`, not a list of token kinds.

## When it is closed

The Fix, Can't come back and Proof bullets state: what the next user or agent experiences on the
normal path, the before and after shape with what changes and why it matters,
the rule now impossible to break, and the type, private API, generator,
compile-fail case, hook or lint that proves it.

The pit is closed only when the valid intent has one discoverable surface,
every known invalid path is absent, private, generated-only or rejected, the
invariant has one owner, every consumer uses it, compile-time and runtime
proof exist where the boundary needs both, and a new agent following normal
discovery has nothing left to remember.

## Upstream issue

When the surface belongs to someone else, file one issue with these sections:

```text
## Repeated friction
## True class of gap
## Single blessed surface
## Bad shape / fixed shape
## Public lanes to remove or make non-namable
## Invariants made unrepresentable
## Contract tests
```

## Example

A test runner exposes:

```text
runner test --engine browser --mode headless --target 123 --reattach --clean-stale
```

1. Bad attempts: `--engine browser --mode headless` is undefined for engines
   without a headless mode; `--reattach` without a live session fails;
   skipping `--clean-stale` after a crash wedges the next run.
2. Who: any agent reading `--help` assembles a plausible but invalid
   combination; the docs tell people the right incantation to memorize.
3. Sibling lanes for "run the tests": `test`, `run`, `check --live`, plus the
   `--engine` and `--mode` matrix.
4. Invariant: engine and mode are determined by the target, not chosen; the
   runner owns the job lifecycle, so stale jobs are its problem.
5. Blessed surface: `runner test <target>`.
6. Hard cut: `--engine`, `--mode`, `--reattach` and `--clean-stale` are not
   namable on `test`; engine selection moves to a read-only `runner diagnose`.
7. Next-agent test: `runner test smoke` has no flag to get wrong, no ritual
   and no hidden precondition. Closed.

Wrong: "Add a JWT scalar, a password scalar, a refresh-token scalar and a
secret-URL-token macro." Right: "Add one sensitive-text surface with movement
rules; hard-cut the overlapping token macros."
