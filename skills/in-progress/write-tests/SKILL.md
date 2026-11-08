---
name: write-tests
description: "Use every time a test is about to be written or edited, in any language and any test framework: a unit, integration, scene, story, snapshot or end-to-end test, a fixture, a factory, a test double, a parametrized table, or a regression test for a bug fix. Also use when deciding whether to keep or delete a test. A test earns its place only if it fails against a plausible wrong implementation and no other test already fails for the same break. Lists the bad tests agents write, each with its fix, and how to prove a test catches its break."
metadata:
  when: "about to write, edit, keep or delete a test"
  situation: Writing code
---

# Write tests

A test earns its place only if it fails against a plausible wrong
implementation, and no other test already fails for that break. Everything
below follows from that one rule. A test that passes whether or not the
behaviour happened says "checked" when nothing was, which is worse than no
test.

## Before writing a test

<what-to-do>
1. **Name the rule** in one sentence: what must be true, and at which public
   entry point. "Checking out a cart in CAD charges the CAD total" names a
   rule; "test checkout" does not.
2. **Break that rule in the code**, in the smallest plausible wrong way: skip
   the request, return the default, swap the currency, drop the write, take
   the other branch.
3. **Run the existing tests of that module.** If one fails, the rule is
   already covered: write nothing. A test's name never shows what it covers;
   an end-to-end test that asserts the final price already checks the
   currency rule, though its name says "creates a product". Only the break
   shows it.
4. **Undo the break.** Write the new test only when nothing failed.
</what-to-do>

For a bug fix, the test is written first and must fail on the code before the
fix. For new behaviour, it fails before the code exists.

## How to write it

- **Test at the public entry point against the real boundary.** Call the
  function, handler or command the caller calls. Use a real database (a
  scratch one), a real library, a real listener, a real temporary directory.
  Internal code always runs for real: give a dependency its own tests and use
  the real one in its caller.
- **Replace only what the test cannot own,** such as a third-party remote API,
  the clock or randomness, and replace it at the edge where the process calls
  out, never an internal wrapper around it. Put the reason beside the
  replacement: what it stands for and why the real one cannot run here.
  "It is easier" or "it is faster" is not a reason.
- **Assert the result only the correct code produces.** The returned value,
  the row written, the response sent, the screen shown. Each kind of failure
  has its own variant carrying its facts (the status code, the missing field,
  the address that refused), and each test asserts its own variant.
- **Fixtures cover every shape a real caller passes.** Before choosing
  fixtures, search every caller of the code under test and list the shapes
  they pass. One fixture per distinct shape. A one-field record stands in
  only when every caller passes a one-field record.
- **An input expected to produce nothing is a near miss.** It shares words,
  tokens or structure with the inputs that do produce something, so it fails
  when the code matches too broadly. A far-off input only fails when the code
  fires on everything.
- **Every assertion in a parametrized test depends on the parameter.** An
  assertion that passes the same for every row goes in its own test.
- **Expected values are stated or read from the table the code reads.** Never
  compute the expected value with the function under test.
- **Use the strongest assertion the claim allows:** the exact value, the
  exact error variant, the whole payload when its shape matters.
- **Name the test for the situation, in plain words.** "A shopper with 3
  points left asks to spend 7 and gets 3, with a notice" describes what
  happens. "decideAllocate rejects with NoPoints" repeats the code.
- **Keep it as small as its claim.** The smallest real input that shows the
  behaviour, in-process, under one second including setup. Wait for the event
  the test needs (a process exit, a written row, a listener accepting), never
  for a fixed number of seconds. Build expensive setup once and share it,
  never per test.

## Tests agents write that catch nothing

| Bad test | What to write instead |
| --- | --- |
| Asserts a mock or spy was called | Assert the result the call was for: the payload sent, the state it left |
| Snapshot of a constant or a config value | Nothing. A snapshot earns its place only for output with a behavioural claim |
| Re-checks what the type checker already refuses | Nothing. The compiler is the test |
| Tests a library's own behaviour | Test your code that uses it |
| Restates the implementation, line by line | Assert what a caller observes |
| Passes when the code returns its default or an empty result | Assert a value only the correct path produces, and give each failure its own variant |
| Replaces an internal module with a fake | Use the real module; replace only the outside effect |
| A catch-all fake that accepts any call | A replacement that offers only the calls the boundary has, and refuses the rest |
| A second test for a break another test already fails on | Nothing. Keep the one at the public entry point |
| A list of literal cases beside a test that checks the whole set | Delete the literal cases |
| A new test appended to a file without saying what it catches that the file does not | Run the break first; write it only if nothing fails |
| A fixture simpler than every real caller's input | One fixture per shape the callers pass |
| A check that could not run, counted as a pass | Report "could not run" as its own result |
| Sleeps for a fixed time, then checks | Wait for the event |

## Prove the test

<what-to-do>
1. **Run the stack's mutation-testing tool** on the module when it has one
   (mutmut or cosmic-ray for Python, StrykerJS for JavaScript and TypeScript,
   cargo-mutants for Rust, PIT for Java, gremlins for Go). It breaks one site
   at a time and records which tests fail, so a test no break fails shows at
   once. A break that fails several tests marks them for a look, not yet as
   duplicates.
2. **Break the rule the test names by hand,** in the smallest plausible wrong
   way. Also break what the test depends on: make the request never arrive,
   the file never open, the service unreachable.
3. **Run the module's tests and read which fail.**
   - Nothing fails: the test cannot fail. Fix it at its cause (step 4).
   - Only this test fails: keep it.
   - This test and another fail: one is a duplicate. Keep the one at the
     public entry point against the real boundary, and delete the other.
4. **Fix a test that cannot fail at its cause.** The cause is usually in the
   code: several failures collapse into one answer ("unavailable", `None`, an
   empty list, a generic error), so the test passes when the request never
   arrived. Split the answer into variants and assert the right one. When the
   assertion is the cause (it checks a default the code returns anyway, or a
   replacement answers before the real path runs), assert the result only the
   correct path produces.
5. **Undo the break** and run the module's tests again; all pass.
</what-to-do>

Done when the test failed on the broken or pre-fix code, passes on the fixed
code, and is the only test that failed for its break.

## When a test fails for the wrong reason

A test that fails under load, on a slow machine or in another order is a bug
in the test. Fix it at once: wait for the event instead of a time, give it its
own scratch resources, remove the shared state. Never retry it, skip it, mark
it slow or raise its time limit.
