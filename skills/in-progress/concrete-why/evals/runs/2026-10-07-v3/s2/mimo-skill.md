The risk isn't the three checks — it's what happens when one of them fails. Hand-rolled validation throws an `Error` the error middleware doesn't recognise, so a bad delivery comes back as a 500 that Stripe retries for three days, instead of a 400 it drops.

**What the error middleware does with each kind of throw**

`src/middleware/errors.ts` is the error handler every Express route's throws pass through. It has exactly one validation-shaped branch, and it matches on type:

```ts
// src/middleware/errors.ts
if (err instanceof ZodError) {
  // ▸ Only errors thrown by zod land here.
  return res.status(400).json({
    error: "invalid_body",
    issues: err.issues.map(i => ({ path: i.path.join("."), message: i.message })),
  });
}
// ...
// default handler: res.status(500) + src/alerts/pager.ts when 500s exceed 5/min
```

So the shape of your validator decides the HTTP status, not you.

**What a hand-rolled validator does on the payload Stripe now sends**

Last week Stripe's docs announced `data.object.customer` can be `null` on guest-checkout events. The naive three-field check rejects it:

```ts
// hand-rolled, inside the new POST /webhooks/stripe handler
if (typeof body.data.object.customer !== "string") {
  // ▸ null fails this, because typeof null is "object".
  throw new Error("customer must be a string");
  // ▸ A plain Error, not a ZodError.
}
```

1. Stripe delivers a guest-checkout event where `data.object.customer` is `null`.
2. The check throws `new Error("customer must be a string")`.
3. `errors.ts` tests `err instanceof ZodError` — false — so the error falls through to the default handler and the response is **500**.
4. Stripe treats 5xx as "try again later" and redelivers with backoff **for up to 3 days**. Every redelivery runs the same check on the same payload and gets the same 500.
5. If enough deliveries arrive in one minute (e.g. a batch of guest-checkout events), the 500s exceed 5/min and `src/alerts/pager.ts` wakes someone up for a payload that will never be valid.

The zod version of the same delivery throws `ZodError`, `errors.ts` returns **400**, Stripe does not retry 4xx, and the event is dropped with a readable issue list. Note the fix isn't "don't reject null" — Stripe announced the change, so the schema should be `z.string().nullable()` and accept it. The point is that whichever way you decide, a hand-rolled rejection travels down the wrong status path.

**What hand-rolling actually saves**

`zod` is already in `package.json` (v3.23) and 14 route handlers already use it, so there is no dependency cost to avoid. What hand-rolling replaces it with is two hand-maintained claims about the same body: the checks and the type:

```ts
// hand-rolled
function validate(body: unknown): WebhookBody {
  const b = body as { id?: unknown; type?: unknown; data?: { object?: { customer?: unknown } } };
  if (typeof b.id !== "string") throw new Error("id must be a string");
  // ...
  return body as WebhookBody;
  // ▸ The cast re-states the checks. Widen a check, forget the cast, and
  //   the type lies about a field the checks no longer enforce.
}

// zod, one claim
const webhookSchema = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
});
type WebhookBody = z.infer<typeof webhookSchema>;
// ▸ The type is derived from the checks; they cannot drift apart.
```

There is one way to hand-roll safely: have the handler return 400 itself instead of throwing. That avoids the 500 path, but then the handler re-implements the issue-list mapping `errors.ts` already provides for the other 14 routes, and the checks-plus-type duplication above still stands.

**What I couldn't confirm:** I read `errors.ts` and confirmed it matches `ZodError` by `instanceof`; I did not find a `ValidationError` base class or a second validation branch, so a custom error class would also fall through to the 500 handler today. I also didn't enumerate whether any of the 14 existing handlers hand-roll validation — if one does, it has this same defect.

**What decides it:** when validation fails, does the delivery get a 4xx (Stripe drops it) or a 5xx (Stripe retries 3 days and on-call can get paged)? Any rejection that isn't a `ZodError` takes the second path, which is the whole argument.
