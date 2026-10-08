Because the 3 checks aren't the risk — the throw type is.

`src/middleware/errors.ts` only maps `ZodError` to 400 `invalid_body`. Anything else you throw becomes a 500, which pages on-call via `src/alerts/pager.ts` at >5/min.

Stripe won't retry a 400, but it retries a 5xx for up to 3 days. So one malformed webhook with hand-rolled `throw new Error()` turns into 3 days of retries and pages.

zod is already a dependency (v3.23, used in 14 routes), so it's 3 lines to stay on the same contract. It also forces us to handle last week's change: `data.object.customer` can now be `null` for guest checkouts, which a `typeof === 'string'` check would 500 on.
