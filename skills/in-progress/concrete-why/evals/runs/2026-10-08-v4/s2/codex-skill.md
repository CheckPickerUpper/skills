The existing error middleware turns a `ZodError` into a structured HTTP 400; an ordinary thrown `Error` becomes HTTP 500. Hand-written validation can work here, but it must also produce the 400 response—checking three fields is only part of the work.

My earlier “same as the other routes” was not a reason. The concrete reason to use zod is how validation failures reach the caller.

For the new `POST /webhooks/stripe` endpoint in `acme/billing-api`, Stripe sends `id`, `type`, and `data.object.customer`. The shared Express error middleware in `src/middleware/errors.ts`, used by route handlers, already converts zod failures into:

```json
{
  "error": "invalid_body",
  "issues": [{ "path": "...", "message": "..." }]
}
```

**With zod**, invalid input reaches that middleware as a `ZodError`, so Stripe receives HTTP 400 and does not retry. Zod v3.23 is already installed, so this adds no dependency.

**With hand-written checks**, we can return that same status and response ourselves. There is no verified failure inherent in doing that. The specific failure happens **if those checks throw an ordinary `Error`**:

1. Stripe delivers a body that fails a field check.
2. Our handler throws `Error`.
3. `src/middleware/errors.ts` sends HTTP 500.
4. Stripe retries the rejected delivery with backoff, potentially for up to three days.
5. If these failures push 500 responses above five per minute, the alert code in `src/alerts/pager.ts` pages on-call.

That turns rejected input into repeated requests and potentially an alert.

There is also a field-contract decision either implementation must handle: Stripe’s documentation now permits `data.object.customer` to be `null` for guest checkout events. A zod string schema and a manual string check both reject those deliveries. Zod does not decide whether this endpoint should accept them.

I don’t have the exact source lines available in the supplied facts, so I can’t reproduce the real code. I also haven’t confirmed which event types this endpoint needs to process, which determines whether rejecting a null customer is appropriate.

I recommend zod because it already reaches the required 400 handler. What decides it is whether rejected input produces that structured 400; manual validation that does so avoids the retry and paging failure too.