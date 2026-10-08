I'd stay with zod. The reason isn't the number of fields. It's what happens when a bad payload arrives.

**What goes wrong if we write the checks ourselves.** Suppose a hand-written check throws an ordinary error, like this:

```ts
if (typeof body.data?.object?.customer !== "string") throw new Error("bad customer");
```

`src/middleware/errors.ts` only turns a `ZodError` into a 400. Any other `Error` goes to the default handler, so this is what follows:

1. One malformed event returns **HTTP 500**.
2. Stripe retries on any 5xx, with backoff, for up to **3 days**. The same bad payload keeps coming back and keeps failing.
3. Those 500s count toward the alert in `src/alerts/pager.ts`. A batch of bad events pushes it past **5 per minute** and pages on-call over a payload that was never going to succeed.

With zod, the same payload gets a **400** with `{ error: "invalid_body", issues: [...] }`. Stripe doesn't retry 4xx responses, so nobody gets paged. That's the same behaviour as the other 14 routes.

We could avoid the throw and send the 400 from the handler ourselves. But then this one route has to copy the `invalid_body` / `issues` response shape by hand and keep it in step with the middleware. Using zod gets that for free.

**A rule that applies either way.** Last week Stripe's docs said `data.object.customer` can be `null` for guest checkouts. A strict `string` check would reject those real events. So the schema needs to allow `null`:

```ts
const StripeWebhookBody = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({
    object: z.object({ customer: z.string().nullable() }),
  }),
});
```

zod is already a dependency (v3.23), so this adds nothing new to the project. If you still want hand-written checks, I'll make them return 400 in the same format and allow `customer: null`. Otherwise I'll go ahead with the schema above.
