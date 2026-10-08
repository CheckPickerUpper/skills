Because here it changes the status code, not just style.

`src/middleware/errors.ts` only maps `ZodError` to 400 `{ error: "invalid_body", issues }`. A hand-rolled `throw new Error` falls through to 500, which pages on-call via `src/alerts/pager.ts` over 5/min — and Stripe retries 5xx for up to 3 days, no retry on 4xx.

So with Stripe now sending `data.object.customer: null` for guest checkouts, a manual `typeof !== 'string'` check would 500 + page + retry instead of a clean 400.

zod is already a dep (v3.23, used in 14 handlers), so it's the same error shape for free.
