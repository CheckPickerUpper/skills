# Data shape: make the bad state inexpressible by shape

Load this once the writer is located and the bad state lives in the shape of
one local state surface (a struct, union, enum, state object, field cluster or
outcome type), or in a type that carves or loosens its source.

The instinct to resist: a brand, guard, validator, `unreachable!()`, default or
normalizer accepts the bad shape and puts a wall beside it. Change the shape so
the bad state has nowhere to be written. The first question is not "how do I
block it?" but "why does this shape allow it at all?"

## The rule

Bugs are representation choices. Removing the choice beats hardening against
the bug. **Model, don't validate.**

- Inspect the **Cartesian product** of related fields before adding guards.
  n independent booleans permit 2^n combinations; the count is a signal the
  shape admits invalid ones. Repeated absence checks usually mean one lifecycle
  is split across loose fields.
- Use a **product type** for data that exists together in one valid state and
  a **sum type** for mutually exclusive states, with each state's fields inside
  its variant. Bundle fields that are created, destroyed or updated together.
- A boolean validator leaves the raw value forgeable and makes every caller
  wonder whether validation happened.

## Carve and loosen: the type is the one source of what the value is

Judge every derived or loosened type with one question: **is this the source
of truth for what the value is, or a shadow cut from something else that will
drift?**

- **Carve:** deriving a subset or variant from a broader type means the
  upstream type carries more than the job needs. TypeScript `Extract`,
  `Exclude`, `Pick`, `Omit`, indexed access `T[K]`, mapped `keyof`; Python
  slicing a `TypedDict` or `cast` to a narrower shape; Rust matching a broad
  enum only to re-wrap one variant a caller should already hold. Fix: shape the
  type where it is built, so what the consumer receives is exactly what it
  needs.
- **Loosen:** weakening a commitment instead of making it. Absence is a real
  state; model it as a named variant (`{ present: true; value: T } |
  { present: false }`), never as optional, null or undefined in a domain type.
  There is no "fine at the boundary" exception: the boundary is exactly where
  absence is parsed *into* a named variant. The rule is on the effect, not the
  spelling: a `?` field, `Partial`, `Required`, `!`, `Optional[T]`,
  `TypedDict(total=False)`, `Any`, `Option<T>` used for "absent for now",
  `unwrap` at a boundary, a nullable column, a default-to-undefined, or any
  helper a codebase invents that yields an optional field. A syntax rule
  catches the tokens; this judgment catches the effect.
- **Two representations of one fact:** a hand-written type beside a runtime
  schema of the same data is step 7 of the protocol. Derive the type from the
  schema.

Not smells: constructions that build or strengthen rather than carve.
`Record<ClosedUnion, V>` (every key forced present), `ReadonlyArray` or
`ReadonlyMap` on built-ins you cannot redeclare, and deriving one type from one
authoritative schema.

## Reshape walk

Read the whole target first: every file the shape touches, and any existing
union, enum or trait the reshape could collide with. A reshape grounded on half
the code breaks an invariant three files away. Then follow these steps in
order. The findings go into the main answer's Root Cause, The Class and
Class Fix sections, written as full sentences.

### 1. Name the bad state concretely

Write one concrete invalid value the current shape allows: "`selectedIndex` is 3 and `slots[3]` is `Empty`", not "the state can be
inconsistent". With no concrete example, stop: the shape may be fine.

### 2. Locate what makes it expressible

Name each field, with its type, whose combination allows the bad state, and
say in a sentence how it contributes. One field alone usually means a value-domain problem (a refinement or parse
boundary). Two or more means a disagreement between fields.

### 3. Classify the smell: pick exactly one

| Smell | Shape | Example |
| --- | --- | --- |
| Index pointer into a collection | An index refers to an element whose state the shape does not check | `selectedIndex` beside `slots`, where `slots[selectedIndex]` may be empty |
| Bool plus optional pair | A flag and an optional value encode one fact twice | `isError: bool` + `errorMessage: string?` |
| Nullable as signal | Null on an internal field stands for a state | `currentUser: User?` meaning "logged out" |
| Redundant derivable field | A field computable from others or from a source elsewhere | `isAdmin: bool` beside `roles` |
| Parallel arrays | Two arrays meant to line up by index | `names[]` + `ages[]` |
| String as enum | Free text with a small fixed set of valid values | `status: string` for pending, active, done |
| Flat flags for a variant | Several flags or optionals that together encode a few variants | `isLoading` + `data?` + `error?`: 8 combinations, 3 valid |
| Collapsing comparator | A function folds an N-variant input into a 2-variant answer, so callers re-derive the lost cases | `compareSlots(a, b): "Same" \| "Different"` over a 4-variant slot |
| Runtime union reclassifier | A switch on a root's kind re-wraps a subset as "found" or "capable" and rejects the rest | `switch (definition.kind)` returning `Capable` for three kinds and `NotCapable` for the others |
| Collapsed outcome | An effectful function's return type names no non-happy state, and two or more different branches leave through it | `cleanCache() -> int` returning nonzero both when a file is held open and when cleanup broke |
| Free-text reason | A failure stores its reason as text standing in for a closed set of causes | `SourceUnavailable(detail: string)` for an unparsable manifest, a missing directory and an unknown repository |

Say which smell it is and the trait that decides it over the others.

### 4. Propose the reshape

Show the current types and the new shape, then say in one sentence why the
step-1 example now has nowhere to be written. Typical moves:

- **Index pointer:** remove the index; put selection inside the element as a
  variant, or hold a direct reference.
- **Bool plus optional, nullable as signal, flat flags:** one sum type with one
  variant per valid combination.
- **Redundant derivable field:** delete it; compute on demand or cache it
  inside its source.
- **Parallel arrays:** one array of records.
- **String as enum:** an enum or discriminated union.
- **Collapsing comparator:** delete it; define the relationship union where the
  values enter the system and switch on it flat. Fix a wrong runtime field type
  at the boundary first.
- **Runtime union reclassifier:** delete it; accept the narrower union at the
  boundary, or split the source type so the consumer receives exactly its
  slice.
- **Collapsed outcome:** a named outcome with one variant per branch the body
  already tells apart (`Emptied | EmptiedExceptHeld | CleanupBroken`), returned
  from every branch and matched by callers. Not a second return value, an
  out-parameter or a comment listing the codes. Not this smell: a predicate
  whose boolean is the fact, a function with one non-happy branch, a process
  exit status handed to the operating system.
- **Free-text reason:** one variant per real cause, each with its own payload
  (a path, an exit code, a repository name). Keep text that arrived from
  outside inside a field that says where it came from (`stderr`,
  `responseBody`), and keep functions that format a sentence from a named case.
  The ban is on storing the reason as text, not on rendering one.

One prescription, never a menu.

### 5. Prove a reshape was considered before any wall

A wall (refinement type, parse boundary, guard) is allowed only when:

- the bad state is a value-domain problem, not a shape problem (an email's
  format, a positive integer); or
- the data crosses a trust boundary (an external API, user input, a stored
  row), where the wide shape is received and narrowed once into a committed
  type; or
- the user explicitly scoped the reshape out (for example, a stored format
  mid-migration).

Say which of the three applies, specifically, and only then name the wall.

### 6. Check nearby code for the same smell

Name each other place with the same smell by symbol or `file:line`, or say
none was found in what you read.

Rejected: skipping the concrete bad state; a type wrapper as the reshape
(`Email<Validated>` around a string still allows every bad string); a runtime
assert as the reshape; "could be either smell"; "the shape is fine, add a
check".
