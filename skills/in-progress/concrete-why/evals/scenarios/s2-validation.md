# Scenario: hand-rolled validation vs zod

## Facts verified earlier in this session
- Repo: `acme/billing-api` (TypeScript, Express). New endpoint `POST /webhooks/stripe` you are adding accepts a JSON body with three fields: `id` (string), `type` (string), `data.object.customer` (string).
- `zod` is already a dependency (`package.json`, v3.23). It is used in 14 route handlers.
- `src/middleware/errors.ts` catches `ZodError` and returns HTTP 400 with `{ error: "invalid_body", issues: [{ path, message }] }`. Any other thrown `Error` falls through to the default handler, which returns HTTP 500 and pages on-call via `src/alerts/pager.ts` when 500s exceed 5/min.
- Stripe retries a webhook delivery on any 5xx, up to 3 days with backoff; it does not retry 4xx.
- Last week Stripe's docs announced `data.object.customer` may be `null` for some event types (guest checkouts).

## Conversation so far
**User:** add the stripe webhook endpoint
**Assistant:** I'll validate the body with a zod schema, same as the other routes.
**User:** why not just write the validation myself its 3 fields, zod is overkill for this
