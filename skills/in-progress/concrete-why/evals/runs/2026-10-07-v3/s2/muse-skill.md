Rejected bodies that go through the validation-error branch leave as 400 with field paths and are dropped; rejected bodies that miss that branch leave as 500, are retried for up to 3 days, and count toward the on-call page. Put the three checks through the validation-error branch so the guest-checkout case fails as a 400.

**How rejected bodies leave the service**

`acme/billing-api`, the TypeScript Express billing service you are adding to, holds 14 route handlers with validation and the new webhook.

`package.json` is the dependency manifest at the repo root that declares what the service installs, which those 14 handlers install from.

`zod` v3.23 is the validation library declared there and already used in those 14 handlers to check request bodies.

`parse()` is the `zod` schema method those handlers call that returns the checked body or throws when the body fails.

`ZodError` is the error type `parse()` throws when validation fails, which the error middleware below checks for with `instanceof`.

`Error` is the built-in error type for any other throw, which skips the 400 branch and falls to the 500 path.

`src/middleware/errors.ts` is the Express error middleware that turns thrown errors into HTTP responses for every route, which all route handlers depend on to set the status code:

```ts
// src/middleware/errors.ts:14
if (err instanceof ZodError) {
// ▸ True only when a zod schema rejected the body.
  return res.status(400).json({ error: "invalid_body", issues: err.issues });
// ▸ Sends 400 with field paths and messages; the sender drops 4xx.
}
// ...
// ▸ Any other Error skips the branch above.
return res.status(500).json({ error: "internal" });
// ▸ Sends 500; these responses are counted toward the paging threshold below.
```

`src/alerts/pager.ts` is the alerting code the default error path calls that pages on-call when 500s exceed 5/min, which on-call waits on for server failures. Nothing thrown as `ZodError` reaches it.

**What the new webhook receives**

`POST /webhooks/stripe` is the new endpoint you are adding that accepts JSON with `id`, `type`, and nested `data.object.customer`, which the event sender calls on each event.

Stripe is the payment processor sending these event POSTs, which retries any 5xx for up to 3 days with backoff and drops 4xx without retry.

Last week's docs change is Stripe's announcement that `data.object.customer` may be `null` for guest checkouts, which this endpoint must now accept as a possible input.

The zod shape throws into the 400 branch:

```ts
// proposed check in the new handler for POST /webhooks/stripe
const Body = z.object({
  id: z.string(),
// ▸ Fails unless id is a string.
  type: z.string(),
// ▸ Fails unless type is a string.
  data: z.object({ object: z.object({ customer: z.string() }) }),
// ▸ Fails unless the nested customer is a string.
});
Body.parse(req.body);
// ▸ Throws ZodError on any mismatch, which errors.ts answers as 400.
```

The hand-written shape throws past it:

```ts
// proposed hand-written check in the new handler for POST /webhooks/stripe
if (typeof req.body.id !== "string") throw new Error("bad id");
// ▸ Throws plain Error, not ZodError, so errors.ts skips the 400 branch.
if (typeof req.body.type !== "string") throw new Error("bad type");
// ▸ Throws plain Error, not ZodError.
if (typeof req.body.data?.object?.customer !== "string") throw new Error("bad customer");
// ▸ Throws plain Error on missing nesting and on null.
```

**What a hand-written throw does on a guest checkout**

1. Stripe POSTs to `POST /webhooks/stripe` with `{"id": "evt_123", "type": "checkout.completed", "data": {"object": {"customer": null}}}` for a guest checkout.
2. The hand check `typeof ...customer !== "string"` is true for `null` and throws `new Error("bad customer")`.
3. `src/middleware/errors.ts` tests `err instanceof ZodError`, gets false, and returns 500.
4. Stripe sees 5xx and retries the same delivery with backoff for up to 3 days.
5. Each retry that still carries `null` returns 500 again and counts toward the 5/min threshold in `src/alerts/pager.ts`, which can page on-call.
6. On-call can see a page for a delivery that matches the new docs, and the endpoint keeps receiving the same delivery for up to 3 days.

This happens only when the body fails the hand check, which now includes every guest checkout with `null` customer. It does not happen when the same body fails as `ZodError`, which returns 400 once with `{ error: "invalid_body", issues: [{ path, message }] }` and is dropped.

**"Its 3 fields"**

A zod schema for this body is the object above plus one `parse()` line, with no status code and no response shape in the handler; `src/middleware/errors.ts` supplies the 400 and the `{ path, message }` entries. Matching that observable behavior by hand means checking `id`, `type`, the existence of `data` and `data.object`, and the type of `customer`, then setting status 400 and building `{ error: "invalid_body", issues: [{ path, message }] }` for each failure, or throwing `ZodError` manually. The hand version carries the status and shape code the middleware already holds.

My earlier "I'll validate the body with a zod schema, same as the other routes." was a convention, not a reason. The reason is the 400 branch above and the retry plus paging that missing it triggers.

**What I couldn't confirm:** I could not confirm current webhook volume, so I can't say a burst of guest checkouts exceeds 5/min, only that each 500 counts toward it.

**What decides it:** whether a rejected body leaves as 400 the sender drops or 500 the sender retries and the pager counts.
