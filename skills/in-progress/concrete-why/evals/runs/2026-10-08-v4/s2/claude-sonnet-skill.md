Zod is not what protects you here; the error path is. A hand-written check is fine for three fields, as long as a bad body ends in a 400 rather than a plain thrown `Error`. Zod gets you that 400 without writing it. I said "same as the other routes" earlier, and that was a convention, not a reason.

**What happens to a bad body today**

`src/middleware/errors.ts` catches `ZodError` and returns HTTP 400 with `{ error: "invalid_body", issues: [{ path, message }] }`. Any other thrown `Error` falls through to the default handler, which returns HTTP 500. That handler pages on-call through `src/alerts/pager.ts` once 500s exceed 5 per minute. Stripe retries a webhook on any 5xx for up to 3 days with backoff, and it does not retry a 4xx.

**If you hand-roll it and throw a plain `Error`**

This is illustration, not the real code:

```ts
if (typeof body.id !== "string" || typeof body.type !== "string" /* ... */) {
  throw new Error("bad body");
  // ▸ Not a ZodError, so errors.ts does not turn it into a 400.
}
```

1. Stripe sends an event whose shape the check rejects.
2. The handler throws, and the default handler returns 500.
3. Stripe treats the 500 as a failure and redelivers the same event for up to 3 days.
4. Each redelivery fails the same way. Once they pass 5 per minute, on-call gets paged.

The same thing happens if the check itself crashes, for example reading `body.data.object.customer` when `body.data` is missing. That is a `TypeError`, which also goes to the 500 handler.

**If you hand-roll it and answer 400 yourself**

You write `res.status(400).json({ error: "invalid_body", issues: [...] })` in the handler. That works and Stripe won't retry. The cost is a second copy of the response shape that `errors.ts` already produces for the 14 zod routes. If that shape changes, this route is the one that doesn't.

**With zod**

```ts
// illustration, not the real code
const Body = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
});
Body.parse(req.body);
// ▸ A bad body throws ZodError, so errors.ts returns the 400.
```

That is about the same length as the hand-written version, and it reuses the existing 400 path. Zod is already a dependency, so it adds nothing to install.

**`customer` can be null**

Last week Stripe's docs announced that `data.object.customer` may be `null` for some event types (guest checkouts). Either approach has to decide this before shipping. `z.string()` and `typeof customer === "string"` both reject `null`. If a guest-checkout event arrives, the endpoint answers 400, Stripe does not retry, and the event is dropped without anyone being paged. That is why the schema above uses `.nullable()`. I have not checked which event types this endpoint will receive, so I can't say how often `null` will occur.

**What I couldn't confirm:** I did not check whether `errors.ts` has any other route to a 400 besides `ZodError`. I'm going on what I read: other errors go to the 500 handler.

**What decides it:** a bad body must end in a 4xx, because a 5xx makes Stripe retry for 3 days and page on-call. Zod already gets you there. A hand-written check has to build that 400 itself. If you still prefer hand-rolling, say so and I'll write it with an explicit 400 response.
