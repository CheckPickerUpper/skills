Three fields are easy to check by hand. The reason I’d use zod here is how validation failures are handled: your middleware turns `ZodError` into a structured 400. A plain thrown `Error` becomes a 500, which makes Stripe retry and can page on-call.

Manual validation could return the same 400 directly, but zod is already installed and handles that path for us.

There’s also a contract change to account for: Stripe now allows `customer: null` for guest checkouts. I’ll accept that in the schema so those valid events don’t fail validation.