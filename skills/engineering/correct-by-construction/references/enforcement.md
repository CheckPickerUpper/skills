# Enforcement: block the intent, not the token

Load this when the work product is enforcement itself (a hook, lint, guard,
schema rule, type restriction, skill, rulebook or agent-behavior rule), when
someone asks to "stop agents from X", or when a guard fired and someone wants
to weaken, exempt or disable it.

The protocol makes a bad code state unwritable. Enforcement aims one level up:
it makes a banned behavior unreachable, by blocking the intent the behavior
serves rather than the one spelling that was seen. Nobody can list every wrong
move one token at a time; the next agent always finds the next route. Block the
intent once and every route to it closes together.

## 1. Name the intent, not the token

State what the caller or agent is trying to get away with, at the highest
level that is still true. The token is one symptom.

| Door you saw | Intent to block |
| --- | --- |
| `any`, an escape cast, an ignore directive | making the type lie so the compiler stops checking |
| a phrase such as "out of scope" | deflecting a correctness issue on a non-correctness ground |
| one unwrapped call inside a supervising loop | the lifeline sharing a fate with the work it supervises |
| a screen-, lifecycle- or feature-named helper | the first consumer owning a capability shared by others |

These are examples, not a token list. Search for other spellings, routes,
names and mechanisms that serve the same intent.

## 2. Strip the example's vocabulary

Quarantine every word inherited from the incident (names, file names, repo
patterns, lifecycle words, commands, screens, frameworks, mechanisms) before
writing the rule. Add one back only after proving it defines the whole
behavior class. A repository that happens to call its setup functions
`install…` does not make `install` class-defining; a bad abstraction named for
one screen is not fixed by banning that screen's name.

## 3. Block the whole class

Design the rule against the intent so every door closes, including unseen
ones:

- **Type lying:** `any`, `as unknown as`, `@ts-ignore` or `# type: ignore`
  without a reason, `cast()`, escape casts, `object` or `Any` returned from a
  domain function: one family, one rule.
- **Correctness deflection:** match the structure (deferral language plus a
  non-correctness justification), not a phrase list; the next agent writes
  "smaller wrinkle" or "only matters if".
- **Shared fate:** make the work physically unable to reach the lifeline
  (separate lanes), so no future call site reintroduces the failure.

## 4. Run the letter check

Before shipping, write out, in sentences: the incident's words; the rule with
those words removed; each word added back and the proof that the whole class
needs it; and the routes still open, or that none remain at this layer. If the
rule blocks the token while the intent is reachable another way, it is a patch:
widen it, or say exactly which lower layer must own the rest. A guard that
quietly blocks one door reads as "covered" when it is not.

## 5. Do not pendulum

Precision is part of correctness. A rule so broad it blocks a legitimate use (a
declared `any` at a real wire boundary, a `# type: ignore` with its stated
reason) enforces a token ("never `any`") instead of the intent ("do not lie").
Leave the honest, declared, boundary-justified use reachable with its reason
or domain type; over-blocking trains people to disable the guard, which reopens
every door.

## Example

"Agents write `any` when they cannot infer a type; ban `any`." A regex for the
literal is the letter: the agent writes `as unknown as Foo` or
`# type: ignore` and keeps lying. The intent is that the type stays honest.
Block the family, route the agent to the real move (model the type, narrow at
the boundary, make the state unrepresentable), then name the doors this layer
cannot catch, such as `Object.assign` onto a typed target or a declaration-file
override, so the next author knows the edge.

## Before weakening a guard

A guard that fires is, by default, a consumer bug: the consumer hit a
deliberate invariant. Overturn that only with proof.

1. Read why the rule exists: its stated reason, the change that introduced it,
   and the tests that pin the rejection.
2. State the invariant plainly, naming the bad state it prevents.
3. Read the consumer code that triggered it, not a memory or an error summary.
4. Conclude it is an upstream gap only when the upstream's own tests or docs
   contradict the rejection, or the upstream explicitly means to support the
   pattern and has no blessed path for it.
5. Never turn the build green by weakening the guard: no ignore paths,
   softening, disabling, fail-open patches or "continue on error".

Lead with one verdict and its plain reason. A consumer bug names the guard,
the invariant, the consumer usage, the defect, the consumer-side fix and what
was read. An upstream gap names the guard, the intended upstream contract, the
proof it contradicts itself, the blessed upstream surface to add or repair, and
how closure will be checked.

Example: a client generator refuses path parameters that carry an issued
secret token, and its test rejects `/invites/{invite_token}`. An app exposing
`GET /invites/{invite_token}` is a consumer bug: move the token into the
request body so it stops leaking through logs, browser history, referrer
headers and cache keys.
