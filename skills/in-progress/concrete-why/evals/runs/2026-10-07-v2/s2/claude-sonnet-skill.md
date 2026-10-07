**Short answer:** Keep zod, but not because 3 fields need a library. A hand-written check is fine only if it returns 400 itself on every bad body. Zod gives you that for free, and a hand-written check makes it easy to miss.

**What goes wrong with hand-rolling**

- **Where an invalid body ends up:** `src/middleware/errors.ts` turns a `ZodError` into HTTP 400. Any other thrown `Error` falls through to the default handler and becomes a 500.
- **Why the status code matters:** Stripe retries every 5xx for up to 3 days with backoff, and never retries a 4xx. A 400 ends the delivery, while a 500 repeats it.
- **How hand-rolled code gets a 500:** a bare `body.data.object.customer` read throws a `TypeError` when `data` is missing. A `throw new Error("bad body")` does the same. Both reach the default handler as a 500.
- **The `customer: null` case:** Stripe's docs announced last week that `data.object.customer` can be `null` for some event types (guest checkouts). A hand-written `typeof customer === "string"` check that throws on `null` would turn every guest-checkout event into a 500. Stripe would resend each one for 3 days, and once 500s pass 5/min, `src/alerts/pager.ts` pages on-call.
- **How zod avoids this:** the failure path is already wired to 400. `customer: z.string().nullable()` also states the `null` decision in one place.

**What hand-rolling would not cost you**

- **Response body:** the `{ error, issues }` shape doesn't matter here, because Stripe ignores the body of a webhook response. Matching it is not a reason to use zod.
- **Dependency:** zod is already installed and used in 14 handlers, so using it adds nothing.
- **Size:** hand-rolled is a few lines, which is about the size of the zod schema. Neither choice saves effort.

**What decides it:** whether an invalid body reliably produces a 400 and not a 500. Zod does that by default. Hand-rolled code does it only if every path remembers to. If you want to hand-roll anyway, I'll write it to return 400 explicitly and accept `null`.
