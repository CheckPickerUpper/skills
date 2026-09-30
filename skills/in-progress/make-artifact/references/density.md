# One page, four densities

Job: "The owner opens this to decide which area of the store admin to fix next."
The same measured facts are drawn four ways. Only the last does the job.

## Overloaded

Every fact is on the first screen, so the reader has to find the decision
themselves.

```text
| Area     | Endpoints | Screens | Open issues | Tests | Last change | Owner | Notes                          |
|----------|-----------|---------|-------------|-------|-------------|-------|--------------------------------|
| Orders   | 34        | 6       | 12          | 18    | 2026-09-02  | —     | refund flow uses legacy client |
| Payouts  | 9         | 4       | 22          | 2     | 2026-07-19  | —     | 4 screens move money, 2 tests  |
| Catalog  | 21        | 3       | 5           | 14    | 2026-09-28  | —     | bulk import unauthenticated    |
... 5 more rows, then 3 paragraphs of caveats
```

## Gutted (overcorrection)

The complaint was density, but the fix deleted coverage. The inventory the
reader asked for is gone.

```text
Fix Payouts next.
It has the most open bugs and the least testing.
```

## Vague (second overcorrection)

The rows are back, but each fact has become a phrase. The reader cannot check
any of it or decide from it.

```text
Payouts   — thinnest against its demand; the riskiest surface
Orders    — mature but carrying legacy weight
Catalog   — healthy, with one sharp edge
```

## Layered

The answer comes first, then one scannable line per area with real numbers and
links, and detail folded below.

```text
Fix Payouts next: 22 open bugs, and 4 screens that move money have 2 tests.

Payouts   9 endpoints · 22 open   #761 can't settle a payout, #774 totals off by one day   ▸ details
Orders    34 endpoints · 12 open  #702 refund calls the retired legacy client               ▸ details
Catalog   21 endpoints · 5 open   #688 bulk import accepts unauthenticated uploads          ▸ details
... one line per remaining area

▸ How these were counted (routes parsed from the router; issues open on 2026-09-30)
```
