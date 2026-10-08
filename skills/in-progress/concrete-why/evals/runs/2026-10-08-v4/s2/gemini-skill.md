A hand-rolled check throws a standard error that pages the on-call engineer and causes Stripe to retry bad payloads for three days. Zod ties the validation failure to the existing error middleware that tells Stripe to drop it immediately.

**"same as the other routes"**
I recommended Zod earlier by saying "same as the other routes". That was a default, not an argument.

**What hand-rolled validation breaks**
Stripe retries a webhook delivery on any 5xx response for up to 3 days; it does not retry 4xx responses.

1. A guest checkout happens. Stripe sends a payload to `POST /webhooks/stripe` where `data.object.customer` is `null` (a change Stripe announced last week).
2. The hand-rolled validation sees the customer is not a string and throws a standard `Error`.
3. `src/middleware/errors.ts`, the Express middleware that catches errors from route handlers, evaluates the error:

```ts
// illustration, not the real code
if (err instanceof ZodError) {
  // ▸ Returns HTTP 400.
  res.status(400).json({ error: "invalid_body", issues: err.issues });
} else {
  // ▸ Falls through to the default handler.
  // ▸ Returns HTTP 500.
}
```

4. Because it is an `Error` and not a `ZodError`, the middleware falls through and returns an HTTP 500.
5. Stripe receives the 500 and schedules a retry, sending the exact same failing payload again for up to 3 days.
6. If 5 guest checkouts arrive in a minute, the 500s trigger `src/alerts/pager.ts`, the module that pages the on-call engineer.

Zod throws a `ZodError`, which the middleware turns into a 400. Stripe sees the 400 and drops the payload without retrying.

**What decides it:** does a rejected body return a 400 or a 500? Zod is already wired to the 400 path; a hand-rolled check falls into the 500 path.
