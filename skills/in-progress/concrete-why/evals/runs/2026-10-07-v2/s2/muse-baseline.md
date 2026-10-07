Stick with zod — it's already the standard in this repo.

Hand-rolled checks won't hit the `ZodError` branch in `src/middleware/errors.ts`, so a bad body would fall through as a 500. That makes Stripe retry for up to 3 days, and risks paging on-call via `src/alerts/pager.ts`. Zod gives you the 400 + `{ error: "invalid_body", issues }` for free, consistent with the other 14 routes.

It also makes the new edge case explicit: `data.object.customer` can now be `null` for guest checkouts, so the schema needs to allow that.
