<what-to-do>
**Short answer:** Use zod. Writing it by hand saves about a dozen lines and puts the endpoint on the error path that 500s and pages on-call, which is the opposite of what a webhook should do.
</what-to-do>

**What hand-rolling actually costs** — the deciding consequence is in `src/middleware/errors.ts`, the error middleware every route's throws go through. It converts `ZodError` into HTTP 400 with `{ error: "invalid_body", issues: [...] }`; **any other thrown `Error` becomes HTTP 500**.

- *If I write the validation by hand and throw on a bad body:* that throw is a plain `Error`, so a malformed delivery gets a 500, not a 400. Stripe retries any 5xx on backoff for up to 3 days, so one bad payload turns into three days of repeated deliveries. If 500s across the API exceed 5/min, `src/alerts/pager.ts` pages on-call — a webhook endpoint that 500s on caller error is a paging source. A 400 is never retried; Stripe drops it and moves on.
- *The one real trap in these 3 fields:* Stripe announced last week that `data.object.customer` is `null` on some event types (guest checkouts). A hand-written check like "customer is a string" rejects those as invalid — so valid events fail. A zod schema writes `customer: z.string().nullable()` and the case is handled in the same place as the other two fields.
- *If I hand-roll and return 400 from the handler myself instead of throwing:* no 500s, but the handler now owns its own error response instead of `errors.ts` — this endpoint's error body can drift from the 14 routes that already report through the middleware, and any client-side handling of `{ error: "invalid_body", issues }` sees two shapes.

**On "zod is overkill" being a label:** it is — I can't turn it into a cost. zod v3.23 is already in `package.json`, so nothing new is installed; a 3-field schema adds no measurable per-request work I can point to. My earlier "same as the other routes" was a convention, not a reason either; the actual reason is the middleware one above.

**What decides it:** which error path a validation failure lands on. A thrown `ZodError` is the only thing `errors.ts` turns into a 400; anything else is a 500, and 500 is exactly what makes Stripe retry for 3 days and on-call pick up the phone.
</what-to-do>
