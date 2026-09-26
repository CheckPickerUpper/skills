---
name: test-failure-triage
description: "Write and run focused tests without fixing implementation failures. Use when the user wants to know whether tests catch a defect and wants each result classified as an implementation bug, test-writing failure, harness failure, or pass, with the expected behavior stated."
metadata:
  short-description: "Write tests, classify failures, and fix nothing"
---

# Test Failure Triage

Use this skill for a test-only investigation: write focused tests, run them
against the existing implementation, and determine what each result means.
This is a diagnosis run, not a repair run.

## Boundary

- The user authorizes changes to test files and test fixtures as part of this
  skill. Do not change production code, product configuration, generated
  product artifacts, lockfiles, or unrelated files.
- Before the first meaningful behavior run, correct only mechanical test
  authoring errors that prevent the suite from executing, such as syntax or
  import errors. Record those edits.
- Once a behavior assertion has executed, freeze both the implementation and
  the test. Do not weaken, delete, skip, reorder, or rewrite a failing test to
  make the result green. Do not change production code.
- If the test itself is wrong, report that as a test-writing failure and say
  what the test should assert or set up. Do not silently repair it and hide the
  original result unless the user explicitly asks for a second test-writing
  pass.
- Do not open issues, create a pull request, or propose a fix as though it was
  applied. Report the evidence and stop after classification.

## Establish the expected behavior first

For every scenario, establish an independent test oracle before writing the
assertion. Read the strongest available sources in this order, adapting to the
project:

1. The user's requirement or domain rule.
2. Public documentation, types, schemas, invariants, and validation rules.
3. Existing tests and named examples that establish the same behavior.
4. Callers and neighboring implementation only to understand the reachable
   state and choose a valid fixture.

Do not derive the expected result by calling the same implementation path that
the test is meant to check. For calculations, use a small independently
computed example or a separate source of truth. If the sources disagree,
report the contract conflict instead of choosing whichever result makes the
test pass.

Before editing, make a compact case table for the scenarios in scope:

| Case | Valid setup | Action | Should be | Why that is the oracle |
|---|---|---|---|---|
| ... | ... | ... | ... | requirement, invariant, or named contract |

Choose cases that exercise the requested behavior and its meaningful
boundaries. Depending on the domain, useful boundaries include empty input,
zero, exact capacity, just below or above capacity, partial resources,
invalid values, ordering, rollback, repeated operations, and caps or overflow.
Do not add cases merely to make the suite look large.

## Write and run the tests

1. Find the project's real test configuration and runner. Use its targeted
   command when available; do not guess a command from a different project.
2. Read the existing test file, fixtures, factories, and direct callers before
   constructing setup. A fixture must be valid for the real call path, not a
   degenerate object that bypasses the behavior under test.
3. Write the smallest suite that covers the case table. Assert observable
   domain behavior and state transitions, including rollback or non-mutation
   when the contract requires it. Avoid assertions that merely repeat a
   private implementation detail.
4. Run the focused suite and capture the exact command, exit status, relevant
   output, and any changed test paths. Run a related suite only when it helps
   separate a local failure from a harness or shared-fixture failure.
5. After a meaningful behavior assertion has run, do not alter either side of
   the comparison. A red result is evidence to classify, not an invitation to
   enter a green phase.

For long-running commands, keep progress updates factual and short. Use the
project's task or process tool when one exists, and describe only actions that
actually happened. These are useful shapes:

```text
Checked task <suite or process name>
Waiting for <suite or process name> execution.
Viewed <path>:<line range>
Edited <path>
Ran command: `<exact command>`
Timed <seconds> seconds
Killed task <name>
Testing the edge cases now.
Waiting for test results.
```

Do not claim a task was checked, timed, killed, or edited unless the tool
reported that event. A timeout or cancellation is evidence about the harness,
not a passing test.

## Classify each case independently

Use one of these labels for every scenario. Do not collapse a mixed suite into
one overall pass or failure.

### PASSED

The test reached the intended behavior, the setup was valid, and the observed
result matches the independently established oracle. State what was observed
and why it demonstrates the contract.

### FAILED (Implementation Bug)

Use this only when all of the following are true:

- The expected behavior is supported by a requirement, domain rule, type,
  schema, or existing contract.
- The fixture and action are valid and reach the real implementation path.
- The assertion checks an externally meaningful result rather than an
  incidental private detail.
- The implementation produces a result that violates the oracle.

Report the broken invariant, the exact observed result, the exact result that
should have occurred, and the implementation path that owns the behavior. Say
why the test is valid before calling it a product bug.

### FAILED (Test-Writing Failure)

Use this when the test is the source of the contradiction. Common causes
include an unsupported expected value, invalid or impossible setup, a fixture
that bypasses the real path, a mock that hides the behavior, a wrong call or
argument shape, an assertion on an incidental detail, an order assumption the
contract does not make, or state leaked from another case.

State:

- what the test claimed;
- what the contract actually says;
- what setup or assertion should have been used; and
- why the failure does not establish an implementation bug.

Do not relabel a product failure as a test-writing failure merely because the
test exposes an awkward or surprising behavior.

### BLOCKED (Harness/Infrastructure)

Use this when the behavior assertion never ran because of a runner failure,
compile error outside the test, missing dependency, environment problem,
unrelated suite failure, timeout, or cancellation. Name the exact blocker and
what must be true for the scenario to become testable. Never count a blocked
case as passed or as an implementation bug.

### INCONCLUSIVE (Nondeterministic)

Use this when repeated runs produce contradictory results and the evidence does
not yet identify whether the product or the test is responsible. Show the run
results, identify the unstable boundary, and say what deterministic observation
would settle it. Do not turn flakiness into a bug verdict.

## Required final report

Lead with the outcome, then give one entry per scenario. Keep the wording
concrete and include the expected behavior even for passing cases:

```markdown
Here are the exact results from running `<command>` against `<target>`:

### 1. <scenario>: PASSED

- **Should be**: <contract outcome>
- **Observed**: <actual outcome>
- **Why**: <what this proves>

### 2. <scenario>: FAILED (Implementation Bug)

- **Should be**: <contract outcome>
- **Observed**: <actual outcome>
- **Broken invariant**: <what the implementation violates>
- **Evidence**: <why the setup and oracle are valid, plus the owning path>

### 3. <scenario>: FAILED (Test-Writing Failure)

- **Should be**: <contract outcome>
- **Test defect**: <what the test got wrong>
- **Correct test shape**: <the setup or assertion that represents the contract>

### Run boundary

- **Tests written or changed**: <paths>
- **Production files changed**: none
- **Fixes applied after the behavior run**: none
- **Harness notes**: <only if relevant>
```

Use the same structure when there is a harness blocker or inconclusive result,
replacing the classification details with the evidence that prevents a stronger
claim. Finish by stating that no implementation fix was applied.
