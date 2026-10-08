Hand-rolling the check makes a bad body return 500 unless you also reproduce the 400 response yourself, and Stripe retries 500s for up to 3 days. I'd still use zod, and this is the concrete reason rather than "same as the other routes", which was a convention, not an argument.

**What happens to a bad body today**

`src/middleware/errors.ts` catches one kind of error, `ZodError`, and returns HTTP 400 with `{ error: "invalid_body", issues: [{ path, message }] }`. Any other thrown `Error` goes to the default handler, which returns 500. When 500s exceed 5 per minute, that handler pages on-call through `src/alerts/pager.ts`. Stripe retries a webhook on any 5xx with backoff for up to 3 days, and it doesn't retry 4xx. The 14 existing route handlers that use zod all take the 400 path.

**Option A: hand-rolled (sketch of what I'd write, not repo code)**

```ts
const { id, type } = req.body;
// ▸ Throws a TypeError on the next line if `data` or `object` is missing.
const customer = req.body.data.object.customer;
if (typeof id !== "string" || typeof type !== "string" || typeof customer !== "string") {
  throw new Error("invalid body");
  // ▸ A plain Error, not a ZodError, so errors.ts does not catch it.
}
```

Here is what the last week's change in Stripe's docs does to this version. `data.object.customer` may now be `null` for some event types (guest checkouts).

1. Stripe sends a guest-checkout event with `customer: null`.
2. The check above sees a non-string and throws a plain `Error`.
3. `errors.ts` doesn't recognise it, so the default handler returns 500.
4. Stripe sees a 5xx and redelivers with backoff, and each retry fails the same way.
5. If enough of these arrive to push 500s past 5 per minute, on-call gets paged for an event the endpoint was never going to accept.

A body with no `data` field fails the same way, through the TypeError.

You can avoid this by hand: catch your own failure and `res.status(400).json({ error: "invalid_body", issues })`. But then this endpoint carries its own copy of the error shape that `errors.ts` already produces for the other 14 routes. If that shape changes, this route won't change with it.

**Option B: zod**

```ts
const StripeWebhook = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
  // ▸ Accepts the null case from Stripe's change, so a guest checkout passes validation.
});
const event = StripeWebhook.parse(req.body);
// ▸ A failure throws ZodError, which errors.ts turns into the standard 400 with `issues`.
```

zod is already in `package.json` (v3.23), so it adds no new dependency. The `.parse` call gives you the 400 for free, and the missing-`data` case becomes a 400 as well.

**What I couldn't confirm:** I don't know which event types Stripe will actually send with a null customer, or what the handler should do with those events. I've made `customer` nullable so they pass validation. If your handler needs a customer, it should decide that after validation and return a deliberate response, not rely on a validation failure.

**What decides it:** the error class of a validation failure decides whether Stripe retries for 3 days or stops. zod produces the class that `errors.ts` maps to 400, and hand-written checks produce a plain `Error` unless you copy that mapping.
