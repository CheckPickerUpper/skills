Hand-written checks on this endpoint return 500 where the existing validation returns 400, so bad bodies get retried for up to 3 days instead of dropped, and a burst of bad bodies can page on-call. Keep the existing schema validation for this endpoint.

**How a bad body becomes a 400 or a 500**

`src/middleware/errors.ts`, the Express error middleware that catches throws from every route handler in `acme/billing-api`, the TypeScript Express repo you are adding to, sorts by error type. `zod`, the schema-validation library already installed at v3.23 and already throwing validation failures in 14 route handlers, produces on failure `ZodError`, its failure object listing one entry per bad field with path and message. When that middleware sees that failure type it returns HTTP 400 with `{ error: "invalid_body", issues: [...] }`. Any other `Error`, the plain throw type hand-written checks use, falls through to the default handler, which returns HTTP 500. `src/alerts/pager.ts`, the alerting code that watches 500s, pages on-call when 500s exceed 5/min. `Stripe`, the sender that POSTs to this endpoint, retries delivery on any 5xx for up to 3 days with backoff and does not retry 4xx.

**What hand-written checks do on this endpoint**

`POST /webhooks/stripe`, the new endpoint you are adding that takes `id` and `type` as top-level strings and `data.object.customer` as a nested string in the JSON body, has to turn a bad body into the 400 shape above to avoid retries. The two shapes compare like this:

```ts
// illustration, not the real code — hand-written checks
if (typeof body.id !== "string") throw new Error("bad id");
// ▸ plain throw, not the failure type the middleware maps to 400
if (typeof body.type !== "string") throw new Error("bad type");
// ▸ same: falls to the default handler, answered 500
if (typeof body.data.object.customer !== "string") throw new Error("bad customer");
// ▸ reads through data and object with no guard; still a plain throw
```

```ts
// illustration, not the real code — zod schema
const Body = z.object({ id: z.string(), type: z.string(), data: z.object({ object: z.object({ customer: z.string() }) }) });
// ▸ declares the three fields and their nesting in one place
Body.parse(body);
// ▸ on a bad field throws the failure type the middleware answers 400 with path and message
```

1. Stripe POSTs to that endpoint with a body where `id` is missing, `type` is a number, or the parent of `data.object.customer` is missing.
2. The hand check throws `Error`.
3. That middleware sees a non-`ZodError` and returns 500.
4. Stripe sees 5xx and schedules retries with backoff for up to 3 days; the same `id` keeps getting 500 instead of one 400.
5. If more than 5 such 500s land in a minute, that alerting code pages on-call.

This happens only when the body fails validation; valid bodies go to the success path either way. My earlier "I'll validate the body with a zod schema, same as the other routes" leaned on "same as the other routes," which is a convention, not a reason. The 400-vs-500 branch above is the reason.

**What the three-fields count misses**

Last week's Stripe docs change, the announcement that `data.object.customer` may be `null` for some event types such as guest checkouts, already breaks a `typeof !== "string"` check for a legitimate body:

1. Stripe POSTs a legitimate guest-checkout event with `data.object.customer: null`.
2. `typeof null` is `"object"`, so the hand check throws `Error`.
3. That middleware returns 500 for a body that should have been accepted.
4. Stripe retries that legitimate event for up to 3 days; each retry gets 500 again.
5. The same paging threshold applies: past 5/min of these, on-call is paged for good traffic.

It happens only for event types that send `null`; other types are unaffected. A missing `data`, the top-level object that holds the parent of `data.object.customer` in this body, fails earlier in the same way: `body.data.object` itself throws `TypeError`, the throw JavaScript produces when reading a property off a missing object, before the `typeof` runs, and that `TypeError` is also a non-`ZodError` answered 500.

**What decides it:** the middleware only maps ZodError to 400; everything else is a 500 Stripe retries.
