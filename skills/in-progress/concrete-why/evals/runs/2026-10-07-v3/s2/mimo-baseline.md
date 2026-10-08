Fair question — but here the cost isn't the 20 lines of validation code, it's which HTTP status your mistakes produce.

**The failure class is different.** If my hand-rolled check throws a plain `Error`, it falls through `src/middleware/errors.ts` to the default handler → **HTTP 500 → on-call pager** (fires at >5/min). Worse, Stripe treats any 5xx as retryable: it will redeliver for **3 days with backoff**. A malformed or unexpected body would turn into a multi-day retry storm plus pages. With a zod schema, `ZodError` is already mapped to **400 with a structured issue list** — which Stripe does not retry. The error middleware is written for exactly this path; hand-rolling means working around the wiring that's already there.

**The shape is already drifting.** Stripe announced last week that `data.object.customer` can be `null` for guest checkouts. That's a one-line change in a schema (`z.string().nullable()` or `.nullish()`), in one place. Hand-rolled, it's scattered `typeof` checks where the null case is easy to miss — and if I miss it, that's precisely the throw-a-500 case above.

**Consistency is load-bearing here.** 14 route handlers already validate with zod, and the error middleware has a dedicated `ZodError` branch to match. A hand-rolled validator for route 15 creates a second validation idiom and a second error path for future readers to reason about.

So: zod is already a dependency (no new cost), the schema is ~5 lines, and it buys the correct status code on bad input — which in this endpoint specifically is the difference between Stripe shrugging and moving on vs. hammering us for three days.

Want me to go ahead and write it that way?
