It's only three fields, and zod isn't about the size of the check. It's about what happens when a check fails.

- **With zod:** a bad body throws `ZodError`. `src/middleware/errors.ts` already turns that into a 400, and Stripe doesn't retry 4xx.
- **With hand-rolled checks:** unless you throw something the error middleware recognizes, a failed check falls through to the default handler. That returns a 500, and Stripe retries 5xx for up to 3 days with backoff. If a burst of bad deliveries passes 5/min, `src/alerts/pager.ts` pages on-call. You could wire a hand-rolled check to return 400 itself, but that's new code duplicating what `ZodError` handling already does, and the other 14 routes would behave differently from this one.

Stripe's announcement last week that `data.object.customer` can be `null` for guest checkouts makes this worse. If a hand-rolled `typeof customer === "string"` check rejects those events, you get one of two failures. They throw a plain error and retry for 3 days, or they get a 400 and are dropped silently. Neither is right, because these are valid events. The schema should accept `null` there:

```ts
const StripeWebhook = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({ object: z.object({ customer: z.string().nullable() }) }),
});
```

That's about the same length as the hand-rolled version, and `.parse(req.body)` gets you the 400 behavior for free. I'm going ahead with zod, with `customer` nullable.
