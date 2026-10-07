You can write it yourself. My earlier “same as the other routes” was not a reason; the concrete benefit is how validation failures reach the HTTP response.

- **With zod:** the existing error middleware turns a `ZodError` into HTTP 400 with field paths and messages. Zod is already installed, so this adds no dependency.
- **With handwritten validation:** throwing an ordinary `Error` produces HTTP 500. Stripe then retries the delivery, potentially for three days; more than five 500s per minute also pages on-call. Handwritten validation is equally viable if it deliberately returns the same 400 response.

There’s also a schema correction: Stripe now permits `data.object.customer` to be `null` for guest checkouts. Requiring a string would reject those events with either approach.

I’d use zod because the 400 handling already exists. **What decides it is the failure response, not the number of fields:** handwritten validation must preserve that response, and either validator must accept the documented null case.