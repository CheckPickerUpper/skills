Zod is the better fit here. The reason isn't the field count. It's what happens when a body fails validation. `src/middleware/errors.ts` treats two kinds of errors differently:

```ts
// src/middleware/errors.ts (current behaviour)
ZodError         → 400 { error: "invalid_body", issues: [{ path, message }] }
any other Error  → 500, and src/alerts/pager.ts pages on-call when 500s exceed 5/min
```

Stripe also handles those two responses differently. It retries any 5xx for up to 3 days with backoff, and it never retries a 4xx.

Here's what a quick hand-written check would look like:

```ts
if (typeof body.data?.object?.customer !== "string") {
  throw new Error("invalid customer"); // not a ZodError → 500
}
```

Stripe's docs said last week that `data.object.customer` can now be `null` on guest checkouts. With the check above, this is what happens on the first guest checkout:

1. Stripe sends the event with `customer: null`.
2. The check throws a plain `Error`, so the middleware returns 500.
3. Stripe retries that same event on a schedule for 3 days, and every retry gets another 500.
4. Several guest checkouts in a short window push the count past 5/min, which pages on-call. Nothing is broken; the code is just rejecting a payload Stripe now considers valid.

You could avoid that by writing `res.status(400).json(...)` by hand. But then you'd be copying the `{ error, issues: [{ path, message }] }` shape that the middleware already builds for the other 14 routes, and that copy could drift. The zod version gets the 400 and the correct shape from the existing middleware:

```ts
const StripeWebhookBody = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({
    object: z.object({
      customer: z.string().nullable(), // guest checkouts send null
    }),
  }),
});
```

That `.nullable()` matters whichever approach we pick. Without it, guest-checkout events would get a 400. Stripe wouldn't retry them, so they would be dropped without anyone noticing. With it, they reach the handler, which can then decide what a customer-less event means for billing.

I'll go ahead with the zod schema above unless you want the hand-written version for some other reason.
