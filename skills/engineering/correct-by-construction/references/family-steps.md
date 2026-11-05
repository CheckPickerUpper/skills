# Family steps

Worked families for protocol step 7. Each row lists the steps every member
passes through, and a bug that shows one of them is written per member.

| Family | Steps every member passes through | A bug that shows a per-member step |
| --- | --- | --- |
| Discount types | eligibility, stacking order, rounding, refund reversal | one coupon rounds differently on refund than at checkout: rounding is written per discount |
| Transaction types | validation, currency conversion, ledger posting, reversal | wire reversals post twice: reversal is written per transaction type |
| Form submissions | validation, submit, server answer, client correction | the client shows "saved" and the server rejected it: the client and server validate with two functions |
| Game abilities | input command, effect lifetime, server answer, client reconciliation, interruption of a running ability | a projectile outlives the phase that fired it: each operation picks its own lifetime |

## Values and code paths

Each family above runs in two places at least once: checkout and refund, quote
and settlement, client and server.

- **Values may differ.** An exchange rate at quote time differs from the rate
  at settlement; another player's position on the client lags the server's.
  The place that owns the fact sends it, and the other place corrects itself.
- **Code paths may not.** Both places convert currency with the same function
  and the same rounding; the client and server run the same validation on the
  same input. A second read of an input, a second copy of a rule, or a branch
  on a state only one place has makes the paths differ.

## Swap test for the wording

Before writing a step into a skill, issue or report, replace the family with
another row of this table. A sentence that stops being true carries the
incident's vocabulary; rewrite it in terms of the step.
