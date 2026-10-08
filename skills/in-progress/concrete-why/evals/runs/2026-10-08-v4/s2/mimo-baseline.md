The argument isn't "the other routes do it" — that's convention, and convention isn't a reason. The reason is the error contract in `src/middleware/errors.ts`:

- A hand-rolled `throw new Error(...)` falls through to the default handler → **500** → `src/alerts/pager.ts` pages on-call once 500s pass 5/min.
- Stripe retries **every 5xx** for up to 3 days with backoff. A single malformed payload that 500s gets redelivered continuously.
- A `ZodError` is already mapped to **400**, which Stripe does not retry. That mapping exists; a hand-rolled check opts out of it.

So the cost of "it's only 3 fields" isn't the field count, it's that every validation failure you throw yourself lands on the paging path instead of the 400 path.

There's also a correctness trap in one of those three fields: Stripe announced last week that `data.object.customer` can be `null` for guest checkouts. The natural hand-rolled check —

```ts
if (typeof body.data.object.customer !== "string") throw new Error("bad payload")
```

— is wrong on exactly that case, and wrong in the expensive direction: guest-checkout events 500, page on-call, and retry for 3 days.

```ts
const WebhookBody = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
});
```

If you genuinely want zero dependency, the hand-rolled version has to throw something `errors.ts` maps to 400 — but then you've rebuilt the one thing zod does here, in the one place where getting it wrong costs a page. zod v3.23 is already installed and 14 handlers deep. Use it.
