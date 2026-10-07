**Short answer:** Use zod for `POST /webhooks/stripe`, same as the other 14 routes.

**Validation errors for this endpoint** — `POST /webhooks/stripe` accepts `{ id, type, data.object.customer }`. How we reject a bad body is decided by two pieces you already have:

* `src/middleware/errors.ts` is the Express middleware that turns validation failures into HTTP responses. It catches `ZodError` and returns 400 `{ error: "invalid_body", issues: [...] }`. Any other thrown `Error` falls through to the default handler, which returns 500.
* `src/alerts/pager.ts` is the module that pages on-call when 500s exceed 5/min. Stripe retries webhook delivery on any 5xx, with backoff for up to 3 days, and does not retry 4xx.

  * *If we hand-roll three `typeof` checks and `throw new Error(...)` on failure:* every invalid webhook body comes back 500. Stripe then redelivers the same bad payload for up to 3 days, and a burst of bad deliveries over 5/min pages on-call. To avoid that you have to re-build the 400 response `errors.ts` already builds for zod.
  * *If we use a zod schema:* an invalid body comes back 400 with `invalid_body`, Stripe drops it, and nobody is paged.

**Guest-checkout shape** — last week Stripe's docs announced `data.object.customer` may be `null` for some event types like guest checkouts. So the schema must accept `null` and the handler must branch on it. If the validator requires a string — hand-rolled `typeof customer !== "string"` or `z.string()` without nullable — a guest-checkout event gets 400, Stripe never retries it, and that order never reaches billing.

**What decides it:** `errors.ts` only maps `ZodError` to 400, so zod gets the correct status code with no new error code.
