The hand-written check would throw errors the existing error handler does not recognize, so every mistake in it becomes a 500 that Stripe retries for up to 3 days instead of a 400 it drops. Validate with zod, and let `src/middleware/errors.ts` — the Express error middleware that turns `ZodError` into HTTP 400 with `{ error: "invalid_body", issues: [...] }` — handle the response.

First, an admission: my earlier line, "same as the other routes", was a convention, not a reason. "The other 14 handlers use zod" would be true of any library the routes happen to use. The recommendation survives, but on what follows.

**What a hand-written validator for these 3 fields has to do**

Illustration, not the real code — this is the shape you would be writing:

```ts
// illustration, not the real code
if (typeof body.id !== "string") throw new Error("bad id");
if (typeof body.type !== "string") throw new Error("bad type");
if (typeof body.data.object.customer !== "string") throw new Error("bad customer");
```

Two things in there decide the outcome, and neither is about validation logic: the throw type (`Error`, which `src/middleware/errors.ts` does not catch) and the traversal (`body.data.object.customer`, which throws `TypeError` when any link is missing).

**1. A malformed body pages on-call instead of returning 400**

1. Stripe (or any sender) posts a body where `data` is present but `object` is missing — a truncated or differently-shaped payload.
2. The validator reads `body.data.object.customer`. `object` is `undefined`, so reading `.customer` on it throws `TypeError`.
3. `TypeError` is not `ZodError`, so `src/middleware/errors.ts` passes it to the default handler.
4. The default handler returns HTTP 500, and `src/alerts/pager.ts` pages on-call when 500s exceed 5/min.
5. Stripe sees a 5xx and retries that delivery with backoff for up to 3 days, adding more 500s each time.

With a zod schema, the same payload is a missing-field issue: `ZodError` → 400 with the field path, Stripe does not retry 4xx, nobody is paged.

**2. The guest-checkout `null` is a wrong guess either way — where it lands is different**

Stripe announced last week that `data.object.customer` can be `null` for some event types (guest checkouts). Whatever you assume about that field, you are guessing from the events you have seen. The two mistakes cost different amounts:

- Hand-written check assuming `customer` is a string: a guest-checkout event throws your `Error("bad customer")`, which falls through to the default handler → 500 → retry loop and possible page. The endpoint also silently stops accepting a real Stripe event type.
- Zod schema assuming the same: the event is rejected as `invalid_body` with a `path` of `data.object.customer` in the response. Wrong, but visible, non-paging, and fixed in one place — the schema, where the fix is `z.string().nullable()` or equivalent.

The fix location matters: the schema is one object, and it is what the 14 other handlers already read to know what a route accepts. A hand-written check spreads the same three facts into `if` statements and a throw type that only this endpoint uses.

**3. The throw type is the whole mechanism, not a detail**

`src/middleware/errors.ts` catches one thing: `ZodError`. Anything else — `Error`, `TypeError`, a string throw — reaches the default 500 handler. So "I'll just write the checks myself" really means "I'll also write my own error type, my own 400 response, and make sure every check throws that and nothing else." That is the wiring you are taking on, and each check is a place to get it wrong once.

**What I could not confirm:** the exact field list of the 400 body beyond `{ error: "invalid_body", issues: [{ path, message }] }`, and whether any caller besides Stripe consumes this endpoint's response — I only know Stripe's retry behavior on the status code. The code shown above is an illustration of the hand-rolled shape, not quoted from the repo; `src/middleware/errors.ts` and `src/alerts/pager.ts` are described as they were verified, not quoted line-by-line.

**What decides it:** which exception your mistake throws. A wrong zod assumption reaches the handler that returns 400; a wrong hand-written assumption reaches the handler that returns 500 and pages.
