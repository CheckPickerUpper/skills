**Short answer:** I'd still use zod. In this repo, hand-written validation can easily turn a bad request into a 500. Zod adds nothing new here because it's already installed.

**Writing it by hand**
- To fail a bad body, the usual move is `throw new Error(...)`. Only the error middleware in `src/middleware/errors.ts` turns a failure into a 400, and it does that only for a `ZodError`. Every other error becomes a 500.
- With a 500, Stripe keeps retrying that delivery with backoff for up to 3 days. Once 500s pass 5 a minute, `src/alerts/pager.ts` pages on-call. One malformed event type could mean days of retries and a page.
- To avoid that, the handler would have to send the 400 itself, with the same `{ error: "invalid_body", issues: [{ path, message }] }` body as the other routes. That's a second copy of the error format, and only this route would have it. If someone changes the format later, this route drifts out of step.

**Using zod**
- It's already in `package.json` (v3.23) and 14 route handlers use it. No new dependency, no extra bundle size.
- A failed parse throws a `ZodError`, so the existing middleware returns the standard 400. Stripe doesn't retry 4xx responses, and nobody gets paged.

**One thing applies either way:** last week Stripe's docs said `data.object.customer` can be `null` for guest checkouts. If we check it with plain `z.string()`, or `typeof === "string"` by hand, those events get a 400. Stripe never retries them, so guest-checkout webhooks would be lost without anyone noticing. I'll write it as `z.string().nullable()`.

**What decides it:** whether a rejected body comes back as a 400 or a 500. Here, only a `ZodError` gets the 400 without extra code.
