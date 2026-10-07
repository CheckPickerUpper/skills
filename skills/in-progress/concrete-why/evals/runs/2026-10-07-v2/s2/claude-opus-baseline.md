Hand-rolling 3 checks would be fine on its own, but here it would change what happens when a bad body arrives. I'll stay with zod unless you want otherwise.

**What changes if we hand-roll it**
- A hand-written check would throw a plain `Error`. In `src/middleware/errors.ts`, a plain `Error` falls through to the default handler, which returns a **500**.
- Stripe retries any 5xx for up to 3 days. So one malformed event would be redelivered again and again, and each failure is another 500.
- More than 5 of those 500s a minute triggers `src/alerts/pager.ts` and pages on-call. A bad payload would look like an outage.
- With zod, the existing middleware already turns a `ZodError` into a **400** with `{ error: "invalid_body", issues }`. Stripe doesn't retry 4xx, so the bad event fails once and nobody gets paged.

To get that behaviour by hand, we'd also have to send the 400 and the `issues` shape from this route ourselves. We'd end up copying what the middleware already does for the 14 routes that use zod.

**Zod costs nothing extra here.** It's already a dependency at v3.23, so this doesn't add a package.

**`customer` can be null, whichever validator we use.** Last week Stripe's docs said `data.object.customer` may be `null` for guest checkouts. If we require a string, those valid events get a 400. Stripe won't retry a 400, so we'd silently lose those events. The schema will be:

```ts
z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
})
```

The handler will then need to deal with a null customer explicitly.
