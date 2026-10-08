You can validate three fields by hand. The reason I’d use zod here is that our error middleware already recognizes `ZodError` and returns a useful 400. If custom validation throws a normal `Error`, it becomes a 500—Stripe retries it, and enough failures page on-call.

Also, Stripe now allows `customer` to be `null` for guest checkouts. I’d accept that in the schema so valid events aren’t rejected.

Zod is already installed; this small schema gets the existing error handling without extra wiring.