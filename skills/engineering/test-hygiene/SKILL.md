---
name: test-hygiene
description: "Load before writing, keeping, deleting or judging a test, and whenever a test passes, a suite is called slow, or a test is reported as weak. Every test must fail when its rule breaks and be the only test that does. Proves both by breaking the rule on purpose: a test that still passes is fixed now, together with the code that hid the failure; a test another test already catches is deleted. Never reports a weak test without fixing it."
short_description: "Each test fails when its rule breaks, and is the only one that does."
allow_implicit_invocation: true
metadata:
  when: "writing, keeping or judging a test"
  situation: Writing code
---

# Test hygiene

A test earns its place by two facts: it **fails when its rule breaks**, and
**no other test already fails** for that break. A test missing the first says
"checked" when nothing was, which is worse than no test. A test missing the
second is repeated work on every run. Both are proved the same way: break the
rule on purpose and watch which tests fail.

## The two failures

- **A test that cannot fail.** It passes whether or not the behaviour
  happened. The usual cause is in the code, not the test: several different
  failures collapse into one answer ("unavailable", `None`, an empty list, a
  generic error), so a test expecting that answer passes when the request never
  arrived, the input was never read or the wrong branch ran. Other causes: the
  assertion checks a default the code returns anyway, the fake answers before
  the real path runs, or the test asserts that a mock was called.
- **A test another test already proves, by proxy.** An end-to-end test that
  asserts the final price already checks the currency rule, though its name
  says "creates a product". A new unit test for that rule adds run time and
  nothing else. Names never show proxy coverage; only a deliberate break does.

<what-to-do>
1. **Name the rule** each test is for, in one sentence: what must be true and
   at which entry point.
2. **Break the rule on purpose,** in the smallest plausible wrong way: skip
   the request, return the default, swap the currency, drop the write, take
   the other branch. Also break what the test depends on, not just what it
   asserts: make the request never arrive, the file never open, the service
   unreachable.
3. **Run the tests of that module** and record which fail.
   - Nothing fails: the test cannot fail. Go to step 4.
   - Only this test fails: it is needed. Keep it.
   - This test and another fail: one is a duplicate. Keep the one at the
     public entry point against the real boundary, and delete the other.
4. **Fix a test that cannot fail at its cause.** When different failures give
   the same answer, the code is wrong: give each failure its own variant
   carrying its facts (the status code, the missing field, the address that
   refused), then have each test assert its own variant. A request that never
   arrives then fails the test, and the log names the real cause. When the
   assertion is the problem, assert the observable result that only the
   correct path produces.
5. **Undo the break,** run the module's tests again, and confirm all pass.
6. **Before writing a new test,** do steps 1 to 3 for its rule against the
   existing tests first. Write it only when nothing else fails for the break.

Done when every test you wrote, kept or judged has its rule, its break, and
the list of tests that failed for that break, and every test that could not
fail is fixed or deleted in the same change.
</what-to-do>

## Never

- Report a weak, unfailable or duplicate test and leave it. Finding it is the
  start of the fix, not a finding to hand over.
- Ask the user whether a test is covered elsewhere. Break the rule and look.
- Say a rule is "probably" tested by something else.
- Keep a test because it might catch something. It catches only what its
  break shows.
- Fix an unfailable test by loosening or deleting it when the code collapsed
  the failures it should tell apart; fix the code.

## Report

One line per test touched:

- `test name`: rule; break used; tests that failed → kept, deleted
  (duplicate of `other test`), or fixed (what changed in code or assertion).

## Example

Wrong:

- Five translator tests pass even when their request never arrives, because a
  failed request gives the same answer they expect. (Reported, not fixed.)
- These five probably have other tests already; I can check if you like.

Right:

- `translates_on_500`: an error reply is reported as unavailable; break: the
  request never sent; failed: none → fixed: the translator records why it is
  unavailable (`ServiceError(500)`, `EmptyReply`, `Unreachable(address)`), and
  the test asserts `ServiceError(500)`. It now fails when the request never
  arrives.
- `prices_manual_item_in_cad`: break: price in USD; failed: this and
  `creates_product_from_scrape` → deleted, duplicate of
  `creates_product_from_scrape`, which checks the same price at the public
  entry point.
