Hand-rolling the validation throws a standard error, which the middleware translates to a 500, causing Stripe to retry bad payloads and page on-call. Use zod so the middleware catches it as a 400.

**What hand-rolled validation breaks**

`src/middleware/errors.ts` is the Express error handler that catches exceptions from all routes. Any error that isn't a `ZodError` falls through to a 500. `src/alerts/pager.ts` is the alerting script that pages on-call when 500s exceed 5 per minute.

```ts
// In the webhook route
if (typeof req.body.id !== "string") {
  throw new Error("Invalid id");
  // ▸ Throws a standard Error.
}

// src/middleware/errors.ts
if (err instanceof ZodError) {
  return res.status(400).json({ error: "invalid_body", issues: err.issues });
}
// ...
// ▸ Standard Errors fall through to here.
return res.status(500).send("Internal Server Error");
```

1. Stripe sends a webhook for a guest checkout, where `data.object.customer` is `null` (added to Stripe's docs last week).
2. The hand-rolled check throws a standard `Error`.
3. `src/middleware/errors.ts` sees it is not a `ZodError` and returns an HTTP 500.
4. Stripe sees the 5xx and retries the exact same invalid payload repeatedly for up to 3 days.
5. When 5 webhook failures happen per minute, `src/alerts/pager.ts` pages on-call.

**What zod does today**

Zod is already a dependency in `package.json` and is used by 14 other route handlers.

```ts
// In the webhook route
schema.parse(req.body);
// ▸ Throws a ZodError if the shape is wrong.

// src/middleware/errors.ts
if (err instanceof ZodError) {
  return res.status(400).json({ error: "invalid_body", issues: err.issues });
  // ▸ Caught and translated to a 400.
}
```

1. Stripe sends the null customer payload.
2. Zod throws a `ZodError`.
3. The middleware catches it and returns an HTTP 400.
4. Stripe sees the 4xx, drops the webhook, and does not retry. Nobody is paged.

**What decides it:** Does the error handler have a type it can catch to separate a bad request from a server crash? A Zod schema provides one; an `if` statement does not.
