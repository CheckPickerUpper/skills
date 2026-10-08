I'd still use zod here, but not for the reason I gave earlier. "Same as the other routes" was a habit, not an argument. The real reason is the error handler: when zod rejects a body, it's already turned into a 400. A check you write yourself turns into a 500 unless you also write the 400 response by hand. A 500 here makes Stripe retry for up to 3 days and can page on-call.

Whichever way you go, the schema has to allow `customer` to be `null`, or guest checkout events get rejected.

**What each kind of error turns into**

`src/middleware/errors.ts` is the Express error handler every route's errors pass through:

- **A `ZodError`** becomes HTTP 400 with `{ error: "invalid_body", issues: [{ path, message }] }`.
- **Any other `Error`** goes to the default handler. That returns HTTP 500 and calls `src/alerts/pager.ts`, which pages on-call once 500s go over 5 a minute.

Stripe treats the two status codes differently. It retries a delivery on any 5xx, with backoff, for up to 3 days. It never retries a 4xx.

**What writing the check yourself costs**

If the check throws a plain `Error`:

1. Stripe sends a body whose `data.object.customer` isn't a string.
2. Your check runs `throw new Error("customer must be a string")`.
3. `errors.ts` doesn't recognise it as a `ZodError`, so the default handler returns a 500.
4. Stripe schedules a retry. The body is the same every time, so every retry fails the same way, for up to 3 days.
5. If enough of these arrive at once (more than 5 a minute), on-call gets paged for a bad request body, not an outage.

To avoid that, the check has to skip `throw` and write the response itself, copying the `{ error: "invalid_body", issues: [...] }` shape by hand. This is an illustration, not real code from the repo:

```ts
// illustration, not the real code
if (typeof body.id !== "string") {
  return res.status(400).json({
    error: "invalid_body",
    issues: [{ path: ["id"], message: "Expected string" }],
  });
}
// ▸ Repeated for `type` and `data.object.customer`, plus checks
// ▸ that `data` and `data.object` exist before reading inside them.
```

That works, but it's a second copy of the 400 format living in this one route. Every other route gets that format from `errors.ts`. Any later change to the format in `errors.ts` won't reach this route.

**What zod costs here**

Zod adds no new dependency. It's already in `package.json` (v3.23), and 14 route handlers use it. The schema for these three fields is about five lines, and a rejected body comes out as a 400 with no extra code.

**`customer` can be `null`**

Last week Stripe's docs announced that `data.object.customer` can be `null` for some event types (guest checkouts). That changes what happens to those events under each approach:

- **Strict string check with zod:** a guest checkout event gets a 400. Stripe doesn't retry a 400, so we never process that event, and nothing alerts anyone.
- **Hand-written check that throws:** the same event gets a 500, Stripe retries it for 3 days, and on-call may be paged.

Neither is right. The field should be `z.string().nullable()`, or the matching `null` check if you write it yourself.

**What I couldn't confirm:** whether the event types this endpoint will subscribe to include the ones where Stripe sends `customer: null`. I've only seen the announcement, not a list of which events it affects.

**What decides it:** which response a rejected body ends up as. Zod gets the 400 from `errors.ts` with no extra code. A check you write yourself has to build that 400 on its own, or it becomes a 500 that Stripe retries and that can page on-call.
