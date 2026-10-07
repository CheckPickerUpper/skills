The downside is losing the one-minute rollback: flipping the flag off resolved two incidents before rollout. After deleting the legacy path, a code rollback would take about 12 minutes to reach production.

My earlier answer was too cautious. You’ve had three weeks at 100% with no incidents, which meets [#882’s cleanup criteria](https://github.com/acme/storefront/issues/882). And keeping it costs 412 lines plus 31 legacy tests adding about 40 seconds to every CI run.

I’d delete it now. The concrete tradeoff is a slower rollback if a checkout problem appears.