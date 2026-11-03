# Unit cohesion: exactly one whole per unit

Load this when the bad state is a boundary between units of delivery: one
whole split across sibling units, independent wholes fused under one name, a
proposed unit whose name is an existing unit's name plus an aspect, or a shared
capability placed under its first caller.

A unit of delivery is anything a consumer adopts as one thing: one install
call, one API client, one command, one schema, one manifest entry, one change.
Cohesion means it contains exactly one whole: everything that cannot exist
without the rest, and nothing that can.

## The failures

- **Aspect split:** one whole delivered as sibling units keyed by an aspect
  (request type, lifecycle phase, input kind, CRUD verb, direction, file
  format, caller category). The consumer assembles the whole from fragments,
  and forgetting one gives a silently incoherent system: a client with
  authentication but no retries, an init with no mandatory finish.
- **Grab bag:** independent wholes fused under one name, so consumers cannot
  adopt one without the others or see what they adopted.
- **False seam:** a general capability placed under its first caller, a
  shared layer importing upward, caller-specific identifiers smuggled into a
  general signature, or responsibilities joined that do not share a lifecycle.
  Name the invariant form, move the mechanism to the shared boundary, leave the
  caller's choice with the caller, and remove the upward dependency.

The aspect split is the common agent failure: the second aspect arrives later,
extending the existing unit feels like scope creep, and a sibling gets minted.
The sibling's name confesses it: the existing name plus an aspect qualifier.

## The name test: run it first

Before creating any exported unit, strip the proposed name to
`<existing-unit><qualifier>`. If `<existing-unit>` exists and the qualifier
names an aspect, not a separable concept, fold the work into the existing
unit.

- `installCartItemRequests` + `installCartCheckoutRequests`: two installs, one
  cart domain.
- `registerAuthHandlers` + `registerRetryHandlers`, when neither is optional.
- `sync-users` + `sync-users-cleanup`, when cleanup is mandatory after every
  sync.
- `WidgetCreateSchema` + `WidgetUpdateSchema` duplicating every field.

## The existence test

For each part, ask both directions:

1. **Is this part meaningful without the rest?** If not, it is an aspect and
   belongs inside. A cart that adds items but cannot check out is not a smaller
   cart; it is a broken one.
2. **Is the rest meaningful without this part?** If yes both ways, it is a
   true sibling; fusing it in would be a grab bag.

Then the consumer view: how many calls, imports or entries does a consumer
need for one working whole? It must be exactly one. More than one is an aspect
split; one call that wires two unrelated wholes is a grab bag.

The only legitimate split of one whole is a hard platform boundary the unit
cannot cross (a client process cannot subscribe to a server bus; a build step
cannot run at runtime). Name it. Convenience, file size, "the first half
already landed" and "the new aspect came later" are not boundaries: fold, and
solve size with internal helpers behind one public unit.

## Audit

1. List the units in scope: every exported install, wiring or register
   function, public surface, command or schema, plus any proposed new one.
2. Group them by whole: shared stems, or parts that fail the existence test
   against each other.
3. For each group of more than one: aspects → aspect split, with the fold (one
   merged name, what dedupes, which callers collapse to one call).
4. For each single unit: independent wholes inside → grab bag, with the split.
5. At write time, run the name test before the code exists.

Report each whole in the main answer's sections, in full sentences: what
breaks today and what the fold or split lets the consumer do; the whole the
consumer means to adopt and the units carrying it now; the verdict (one unit,
aspect split, grab bag or false seam) with the existence test both ways; the
consumer's calls today against the one it should need; and the merged or
extracted unit, naming any platform boundary that forces a split.

Do not pendulum: two units that are each meaningful alone stay separate.
Cohesion is exactly one whole per unit, not fewer units.

## Example

A server had `installCartItemRequestsServer` (add and remove) and gained
`installCartCheckoutRequestsServer` (pay and confirm). A cart that holds items
but cannot check out, or checks out with no items, is incoherent: both
directions fail, so these are aspects of one cart request surface. Consumers
paid two install calls and two adapters per storefront, and forgetting one
gave a half-working cart with no error. Verdict: aspect split; fold into one
`installCartRequestsServer` with one subscription contract, removing the
duplicated resolve logic both carried. The client half stays separate only
because a client process cannot subscribe to a server bus.
