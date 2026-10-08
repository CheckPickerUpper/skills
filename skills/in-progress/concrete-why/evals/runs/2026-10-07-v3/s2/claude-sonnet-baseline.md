You can hand-roll it. For three fields the code would be about the same size. What decides it is what happens when a bad body arrives.

`src/middleware/errors.ts` turns a `ZodError` into a 400 with `{ error: "invalid_body", issues }`. Any other thrown `Error` goes to the default handler, which returns a 500. If your hand-written check does `throw new Error("bad body")`, a malformed request gets a 500. Stripe retries every 5xx with backoff for up to 3 days, and the pager fires once 500s pass 5/min. One bad payload could then be retried for 3 days and page on-call along the way. You can avoid that by writing the 400 response yourself in the handler, but then this route has its own error format instead of the shared one.

Zod also adds no weight, since it's already a dependency and 14 other routes use it. The schema is about as short as the manual checks:

```ts
const StripeWebhook = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string() }) }),
});
```

There's one thing to decide either way. Stripe's docs now say `data.object.customer` can be `null` for guest checkouts. With the schema above, or with a hand-written `typeof customer === "string"` check, those events get a 400. Stripe doesn't retry 4xx, so those events would be dropped silently. If you want to accept them, the schema becomes `customer: z.string().nullable()` and the handler has to cope with a missing customer.

I'll use zod with `.nullable()` on `customer`, so malformed bodies get the existing 400 and guest-checkout events are accepted. If you'd rather reject guest checkouts, tell me and I'll drop `.nullable()`.
