If we hand-roll the validation and throw a standard `Error`—or if we miss that `data.object.customer` can now be `null` and cause a runtime crash—it will fall through to the default error handler in `src/middleware/errors.ts` and return an HTTP 500.

When Stripe sees a 500, it retries the webhook for up to 3 days. If those retries push us over 5 errors per minute, it will page the on-call engineer for what is actually just a bad payload.

The middleware is explicitly wired to catch a `ZodError` and return an HTTP 400. This correctly tells Stripe to drop the bad request without retrying. We should use Zod to guarantee that validation failures map to the correct HTTP status and don't trigger incident alerts.
