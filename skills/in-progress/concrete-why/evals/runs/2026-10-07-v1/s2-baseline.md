I'd stay with zod. Three fields is small, but zod isn't about how much validation there is here. It's about what happens when validation fails in this app.

- **Failures already return the right response.** `src/middleware/errors.ts` turns a `ZodError` into a 400 with `{ error: "invalid_body", issues: [...] }`. If the validation is hand-written and throws a plain `Error`, the default handler returns a 500 instead. That has two costs:
  - Stripe retries any 5xx for up to 3 days, so one bad payload keeps coming back.
  - More than 5 errors a minute pages on-call through `src/alerts/pager.ts`, so a burst of bad webhooks wakes someone up.
- **Hand-written validation would copy the error format.** To get a 400 without zod, the handler would have to rebuild the `invalid_body` / `issues` shape itself. That's a second copy of the format, and it can drift from the middleware.
- **It adds nothing new.** zod 3.23 is already a dependency and 14 route handlers use it. A hand-written check would be the one route that validates differently.

One thing matters more than the zod question. Last week Stripe said `data.object.customer` can be `null` for guest checkouts. If the schema requires a string, those events get a 400. Stripe doesn't retry 4xx responses, so those events would be lost without any alert. I'll make the field `z.string().nullable()` and handle the `null` case in the handler:

```ts
const StripeWebhookBody = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({
    object: z.object({ customer: z.string().nullable() }),
  }),
});
```

If that works for you, I'll go ahead with this.
