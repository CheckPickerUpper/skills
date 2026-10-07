Fair question, but the deciding fact is `src/middleware/errors.ts`, not the field count:

**The only error that becomes a 400 is a `ZodError`.** Anything else you throw falls to the default handler → HTTP 500 → and at >5/min that pages on-call via `src/alerts/pager.ts`. So a hand-rolled `throw new Error("invalid body")` doesn't just return the wrong status — it's a paging hazard.

**And Stripe treats those two cases very differently.** 500 → Stripe retries the same event for 3 days with backoff, so one validation bug becomes a persistent retry flood hitting your logs, your pager, and any handler side effects that already ran. 400 → no retry, clean drop.

**The "it's 3 fields" count is off on the part that bites.** Last week's Stripe docs say `data.object.customer` can be `null` for guest checkouts. Hand-rolled, the natural check is `typeof body.data.object.customer === "string"` — which rejects those events, throws a generic `Error`, and turns every guest-checkout webhook into the 500/retry/pager scenario above. With zod the right shape is stated where you can read it:

```ts
const WebhookBody = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({
    object: z.object({
      customer: z.string().nullable(), // null for guest checkouts
    }),
  }),
});
```

Wrong input → `ZodError` → 400 with `{ error: "invalid_body", issues }` → Stripe drops it and your existing clients get the error shape they already handle.

Yes, zod is already a dependency (v3.23) and 14 route handlers use it — that makes this consistent, but it's the weakest argument here. Even if zod weren't installed, you'd be re-deriving an error type your middleware already understands, and any mismatch silently upgrades bad input into pager noise.

If you still want zero-dep, the honest alternative is hand-rolled validation **plus** throwing a `ZodError`-shaped error (or refactoring the middleware to accept a shared `InvalidBodyError`) — but at that point you've built a worse zod. Want me to go ahead with the zod version?
