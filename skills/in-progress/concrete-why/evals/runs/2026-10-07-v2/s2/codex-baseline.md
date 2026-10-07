Three fields are easy to validate by hand. The reason to use zod here is the existing error handling: a `ZodError` becomes a structured 400; an ordinary thrown `Error` becomes a 500. Stripe retries those 500s, and enough of them page on-call.

Manual validation would work if we explicitly return the same 400 response. Since zod is already installed and used in 14 handlers, it’s less code to get that behavior.

Also, Stripe now allows `customer: null` for guest checkouts. We need to handle that deliberately whichever validator we use.