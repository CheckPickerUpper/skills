Three reasons specific to this repo:

1. **Error handling and on-call alerts**: `src/middleware/errors.ts` specifically catches `ZodError` to return a `400 Bad Request`. If hand-rolled validation throws an unhandled error or `TypeError`, it hits the default `500` handler—which triggers an on-call page via `src/alerts/pager.ts` if there are >5/min.
2. **Stripe retry behavior**: Stripe retries deliveries for up to 3 days on `5xx` responses, but stops on `4xx`. A clean `400` from `ZodError` prevents bad payloads from creating retry storms and false pages.
3. **Payload edge cases**: Stripe recently updated `data.object.customer` to be nullable for guest checkouts. A Zod schema (`z.string().nullable()`) explicitly models this without needing nested null checks, and `zod` is already in `package.json` used across 14 existing routes.
