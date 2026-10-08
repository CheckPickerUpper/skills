Zod is a few lines here, and it means a bad body gets a 400 instead of a 500. That difference matters for this endpoint.

**Why the error type matters:**
- `src/middleware/errors.ts` turns a `ZodError` into a 400 with `{ error: "invalid_body", issues }`.
- Any other thrown `Error` becomes a 500, and Stripe retries every 5xx for up to 3 days.
- Once 500s pass 5/min, `src/alerts/pager.ts` pages on-call.

A hand-rolled check like this would take the 500 path:

```ts
if (typeof body?.data?.object?.customer !== "string") {
  throw new Error("invalid body");   // falls through to the default handler: 500, Stripe retries, pager
}
```

A malformed delivery would then retry for 3 days and could page someone. To get the 400 you'd have to return it by hand in this handler, and nothing would make the next person do the same.

**The schema:**

```ts
const StripeWebhook = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
});

const event = StripeWebhook.parse(req.body); // ZodError -> existing 400 handler
```

Stripe's docs announced last week that `data.object.customer` can be `null` for some event types (guest checkouts), so the schema marks it `.nullable()`. A plain `z.string()` or `typeof === "string"` check would reject those events with a 400. Stripe doesn't retry 4xx, so they'd be dropped permanently.

Zod is already a dependency and used in 14 handlers, so this adds no new weight. If you still want to hand-roll it, I'll write the check to return the same `invalid_body` 400 explicitly, and it must accept `null` for `customer`. Which do you want?
