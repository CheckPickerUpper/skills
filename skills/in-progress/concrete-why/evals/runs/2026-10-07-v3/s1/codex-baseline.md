The downside is slower rollback: flipping the flag off took about 1 minute in the two earlier incidents; after deletion, a rollback deploy would take about 12 minutes.

But my earlier recommendation was too cautious. The new flow has had three weeks at 100% with no incidents, meeting [#882’s cleanup criteria](https://github.com/acme/storefront/issues/882). Keeping the fallback also costs 412 lines of legacy code and 31 tests that add about 40 seconds to every CI run.

I’d delete the flag and legacy path now. The concrete tradeoff is giving up the one-minute fallback.