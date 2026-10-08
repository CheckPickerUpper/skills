The existing error middleware turns a `ZodError` into HTTP 400, but another thrown `Error` into HTTP 500. You can write the three checks yourself; the concrete requirement is that invalid input reaches the 400 response, because Stripe retries 5xx deliveries.

My earlier “same as the other routes” was not a reason. Zod’s benefit here is that its validation errors already reach the response handler this endpoint needs.

In `acme/billing-api`, `src/middleware/errors.ts` is the Express middleware that handles route errors. It returns `{ error: "invalid_body", issues: [{ path, message }] }` for a `ZodError`. Other thrown errors reach the default 500 handler; `src/alerts/pager.ts`, the on-call alert code, pages when 500s exceed 5/min.

Handwritten validation would cause a problem **if it throws an ordinary `Error` for invalid input**:

1. Stripe sends a body that fails one of your checks.
2. The webhook handler throws `Error`.
3. The error middleware returns HTTP 500.
4. Stripe retries that delivery with backoff, for up to three days.
5. If those failures push 500s above 5/min, on-call gets paged.

Handwritten checks that return the expected 400 response avoid that sequence. I have no verified reason they cannot work. Zod is already installed at v3.23 and used by 14 route handlers, so using it adds no dependency and connects these checks to the existing error handling.

There is also a separate decision about the new webhook’s customer field. `POST /webhooks/stripe` currently requires strings for `id`, `type`, and `data.object.customer`, but Stripe announced last week that guest-checkout events can have a null customer. Under either implementation:

1. Stripe sends such an event.
2. String-only validation rejects it with HTTP 400.
3. Stripe does not retry it, so that delivery receives no further processing.

We need to decide whether this endpoint should process those events before choosing string-only validation.

I cannot quote the actual source lines because the supplied record contains verified behavior, not code excerpts. It also does not establish which event types this endpoint should process.

What decides it is whether the handwritten checks produce the required 400 response and accept the events we intend to handle. If they do, the verified facts give me no concrete reason to rule them out.