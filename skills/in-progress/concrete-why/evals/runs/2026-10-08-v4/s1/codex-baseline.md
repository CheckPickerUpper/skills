The downside is slower recovery if the new checkout breaks: flipping the flag restored the old flow in about 1 minute during two previous incidents. After deletion, a code rollback would take about 12 minutes to reach production.

I overstated the case for keeping it. The legacy path costs 412 lines to maintain and adds about 40 seconds to every CI run. You’ve also met [#882’s removal criteria](https://github.com/acme/storefront/issues/882): roughly three weeks at 100% with no incidents.

I’d remove it now. The concrete tradeoff is giving up that fast fallback in exchange for simpler code and faster CI.