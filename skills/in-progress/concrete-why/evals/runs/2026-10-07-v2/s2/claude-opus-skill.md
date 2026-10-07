**Short answer:** I'm keeping zod, but not because the other routes use it. That's what I said before, and it wasn't a reason. The real reason is how the error middleware treats a bad body. A `ZodError` becomes a 400. A plain thrown `Error` becomes a 500, and a 500 makes Stripe retry and can page on-call.

**What happens to a bad body in each case**

`src/middleware/errors.ts` is the shared Express error handler. It has two paths:

- A thrown `ZodError` returns **400** with `{ error: "invalid_body", issues: [{ path, message }] }`.
- Any other thrown `Error` returns **500**. `src/alerts/pager.ts` pages on-call once 500s go above 5 per minute.

Stripe retries a delivery on any 5xx for up to 3 days with backoff. It does not retry a 4xx.

- **With zod:** a malformed delivery gets a 400 that names the bad field. Stripe drops it, nobody is paged, and the logs show which path failed.
- **With hand-rolled checks that `throw new Error(...)`:** the same delivery gets a 500. Stripe keeps resending it for 3 days. A burst of bad events, or one event type whose shape we got wrong, pushes past 5 per minute and pages whoever is on call over a client-side problem.
- **With hand-rolled checks that send `res.status(400)` themselves:** this avoids the 500 path. But it's now a second 400 format, different from the `invalid_body` / `issues` body the other 14 handlers return, written and maintained in this one route.

**What zod costs here:** nothing new. It's already in `package.json` (v3.23), so there's no added dependency or bundle size. The schema is about the same length as three `typeof` checks.

**One thing to get right either way:** last week Stripe announced that `data.object.customer` can be `null` for guest checkouts. If we validate it as a required string, those events get a 400. Stripe never retries a 400, so the events are lost without anyone noticing. The field has to be `z.string().nullable()`, or the equivalent if hand-rolled, and the handler has to deal with a null customer.

**What decides it:** whether a bad body leaves this route as a 400 or a 500. Zod gives the right status and the shared error format without extra code. Hand-rolled checks only get there by duplicating what the middleware already does.
