Writing the checks by hand works only if your code also sends the same 400 response that `src/middleware/errors.ts` already builds for zod errors. The easy way to hand-roll it is to throw a plain `Error`. That turns a bad body into a 500, and Stripe redelivers anything that gets a 5xx for up to 3 days. So I'd keep zod. There's a separate fix both versions need: `customer` has to accept `null`.

My earlier reason, "same as the other routes", wasn't a reason. These are the real ones.

**What happens to a bad body today**

`src/middleware/errors.ts` is the Express error handler shared by every route in `acme/billing-api`.

- When it catches a `ZodError`, it returns HTTP 400 with `{ error: "invalid_body", issues: [{ path, message }] }`.
- Any other thrown `Error` goes to the default handler. That returns HTTP 500, and if 500s go above 5 per minute, `src/alerts/pager.ts` pages on-call.

The 14 route handlers that already use zod get the 400 behaviour just by calling `.parse()`.

**Option A: hand-rolled, written the obvious way**

```ts
// proposed, not in the repo
const { id, type, data } = req.body;
if (typeof id !== "string" || typeof type !== "string"
    || typeof data?.object?.customer !== "string") {
  throw new Error("invalid webhook body");
  // ▸ Not a ZodError, so errors.ts treats it as a crash and returns 500.
}
```

Here's what happens when Stripe sends a body this check rejects:

1. Stripe POSTs to `/webhooks/stripe`.
2. The check throws, and `errors.ts` returns 500.
3. Stripe treats a 5xx as "try again later" and redelivers with backoff for up to 3 days.
4. Each redelivery fails the same way. If enough fail to push 500s above 5 per minute, on-call gets paged for a body that will never pass.

To avoid this, the hand-rolled version has to write the 400 itself: `res.status(400).json({ error: "invalid_body", issues: [...] })`, with the `path` and `message` entries built by hand. That's possible. It also makes this the one route that builds that response shape itself instead of getting it from `errors.ts`.

**Option B: zod**

```ts
// proposed
const StripeWebhookBody = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
  // ▸ .nullable() so guest-checkout events pass (see below).
});
const body = StripeWebhookBody.parse(req.body);
// ▸ On failure this throws ZodError, so errors.ts returns 400.
// ▸ Stripe does not retry a 4xx, so there are no redeliveries and no page.
```

**"Overkill"**

zod is already in `package.json` (v3.23), so this adds no new dependency. The schema is four lines, about the same as the hand-written `if`.

**The part both options need: `customer` can be `null`**

Last week Stripe's docs said `data.object.customer` may be `null` for some event types, such as guest checkouts. If the check requires a string, here's what happens to a guest-checkout event:

- With Option A as written, it gets a 500. Stripe redelivers it for 3 days, and it can page on-call.
- With zod and `z.string()` (no `.nullable()`), it gets a 400. Stripe never retries it, so that event is lost and nobody is told.

Either way, the check must accept `null`.

**What I couldn't confirm:** I don't know which Stripe event types this endpoint will receive, so I can't say whether guest checkouts will actually reach it. I haven't seen how the handler should treat a `null` customer once it gets past validation.

**What decides it:** whether a rejected body comes back as a 400 or a 500. Stripe stops on a 400 and keeps retrying on a 500. zod gives you the 400 through the existing error handler. Hand-rolled code only gives it to you if you remember to write it.
