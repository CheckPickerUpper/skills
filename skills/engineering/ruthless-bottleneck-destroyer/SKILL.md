---
name: ruthless-bottleneck-destroyer
description: "Use before writing, keeping, deleting or judging a test; whenever a test passes or is reported as weak; when tests, checks, builds, hooks, a push gate or a CI pipeline are slow; whenever the user sets or changes a time limit for a test or a check, asks why something is slow, what takes so long, where the time goes or why work takes so long to land, or asks for the slow tests; before running any test suite, build, check or review; and before any status update, summary or handoff that accounts for time. Every check must have something to catch, catch its break, be the only check that does, run only when its inputs change, and cost only what its claim needs. Deletes checks with nothing to catch, proves catching and uniqueness by breaking the rule on purpose, removes repeated work and each slow thing's shared cause at its owner for every checkout, makes the slow shape unwritable at its owner instead of adding a check for it, and keeps going until everything meets the bar. Never reports a weak or slow test without fixing it, never fakes a speed-up, never throws hardware at repeated work, never reports machine load."
short_description: "Every check has something to catch, catches its break, is the only one that does, runs only when its inputs change, and costs only what its claim needs."
allow_implicit_invocation: true
metadata:
  when: "writing or judging a test, something is slow, the user sets a time limit, before running a check, or when accounting for time"
  situation: Writing code
---

# Ruthless bottleneck destroyer

A check earns what it costs. Every test, hook, gate and CI job has five
properties, each with its own proof:

| Property | Bad state | Proof |
| --- | --- | --- |
| **It has something to catch** | a check of code nothing uses; a check repeating what a tool in the gate already refuses; a check standing in for a type, import, schema or generator that would make the bad state impossible to write | a search of every place a user could live finds one; the break gets past every tool; a stated reason the owner upstream cannot refuse it |
| **It catches its break** | a test that passes whether or not the behaviour happened | break the rule on purpose; the test fails |
| **It is the only one that does** | two tests, or two stages, prove the same thing | the same break: exactly one test fails |
| **It runs only when its inputs change** | reruns on unchanged code, coarse cache keys, a second checkout rebuilding | an unchanged rerun does zero work; one changed input redoes only its own unit |
| **It costs only what its claim needs** | setup rebuilt per test, sleeps, process spawns, hardware thrown at repeats | the per-test time limit the runner enforces, and a check that refuses each slow shape |

A check with nothing to catch is deleted, along with any dead code it guards;
when the rule can move upstream, move it there and delete the check. A check
that does not catch its break says "checked" when nothing was, which is worse
than no check. A check missing any other property is time paid for nothing.
The job ends when every check has all five, the cause of each failure is fixed so it cannot
return, and the result reaches every checkout. Until then there is nothing to
report.

## Before running a check

Before running a test suite, build, check or review, ask: **what wrong
behaviour does this run catch that nothing cheaper already catches?** Name the
behaviour, the boundary the run exercises and what would make it fail. Read
what the command really runs, nested scripts included; its name, its length or
its presence in an old brief does not answer the question.

- **Run on current code.** Before a long run, check that the checkout holds
  the development branch's latest commits. A run on a stale checkout measures
  code that is already gone; update it first.
- **Reuse a result that still covers the claim.** When the same commit,
  inputs, environment and dependency versions already passed, read that result
  instead of running it again. Run again only when one of those changed, and
  say which. Read a recorded output instead of rerunning it to check its
  author.
- **Run the smallest check that catches it,** at its real boundary: the
  affected tests, not the whole suite. A change that only deletes code a search
  shows nothing imports needs no test run. Two configurations that select the
  same tests add nothing.
- **Finish cheap iteration first.** Focused runs and reviews come before the
  one expensive run, and a re-review compares with the last reviewed commit.
- **Retry only what can change** without changing the command: a dropped
  network connection can; a wrong argument or a quota refusal cannot.
- **A check the repository requires runs as configured** until the change
  that removes the requirement lands. Never switch a check off, weaken it or
  re-enable one the user turned off to save time.

Each run you decide on is `run`, `narrow` (the smaller check named), `reuse`
(the earlier result named, with its commit), `omit` (with what already covers
it) or `wait` (naming what it waits for and who owns that).

## The bar

- The bar is two limits: the most one test may take, and the most one full
  check may take (every hook, gate or CI job the repository runs before code
  lands). Both are recorded once in the repository, in the per-test judge's
  config (step 1 of making it fast), with one line in its agent rules file
  pointing to it. The judge reads them; nothing else holds a copy.
- When the repository has no bar, ask the user for both limits once, before
  starting, and suggest very fast ones: the fastest the stack could plausibly
  reach when nothing repeats, not today's times rounded down. An in-process
  test takes milliseconds, so suggest a per-test limit well under a second,
  and a full check of a few seconds. Record the answer and start. This is the
  only question the job asks.
- When the user changes the bar, change the recorded value; it applies from
  the next run.
- The bar is a ceiling, not the goal. The goal is the floor: the fastest the
  design allows once no work repeats. A test just under the bar that still
  redoes unchanged work is not done.
- A test's time is what it costs to run, setup included: a fixture, a server
  boot, a migration replay or a build it waits for counts against it.
- There is no slow lane, no `slow` tag, no raised timeout and no skip. A test
  over the bar is made fast or deleted. A declared timeout above the bar is the
  author saying the test may take that long; treat it as a measured offender.
- A gate or check over the bar is itself a bottleneck. Never say "while the
  gate runs" about a gate that breaks the bar; fix it or delete what it
  repeats.

## Never

- **Report a weak, unfailable, duplicate or slow check and leave it.**
  Finding it is the start of the fix. Telling another agent to stop is not a
  fix either.
- **Return before the bar is met.** No timing table, no "next thing to cut",
  no "these stay as they are", no asking whether to continue or which repeats
  to remove. Every return costs the user a turn.
- **Say "unconfirmed", "not checked" or "probably"** about anything you can
  read or run, and never ask the user whether a rule is covered elsewhere.
  Break the rule and look.
- **Keep a test because it might catch something.** It catches only what its
  break shows.
- **Delete a check without the break proof.** A check is redundant only when
  breaking its rule fails another check that stays.
- **Fix an unfailable test by loosening or deleting it** when the code
  collapsed the failures it should tell apart; fix the code.
- **Fix one test at a time** when its cause is shared. Name the class first.
- **Count an open issue as the fix.** "Issue #N already requires it" leaves
  the slow check running. The fix lands now, as the next thing you land.
- **Queue the speed fix behind the work that pays for it.** When queued
  commits each pay a slow gate, test or landing step, the commit that makes
  it fast lands first, ahead of every one of them.
- **Fake the number.** No moving work out of the timed region, no splitting a
  slow test into several just under the bar, no caching that skips the
  assertion, no tuning to a hair under the bar. Fix the slow algorithm, the
  slow design or the slow tool.
- **Throw hardware at it.** Parallel subtests, more workers, more build
  slots, more cores or a bigger machine spread the same work wider and remove
  none of it; the time comes back on a busier machine. They are allowed only
  after every remaining unit of work is accounted for and none repeats (step
  7), and never reported as the fix.
- **Hand-roll a mechanism this skill prescribes.** Breaking code on purpose
  is mutation testing, per-test timing and limits belong to the runner's
  reporter and hooks, and shared templates, locks and caches have maintained
  owners too. Name the standard tool for the stack and use it; write your own
  only when a search shows none fits, and say which you checked.
- **Cut parallelism to make a repeat fit.** Fewer workers or a lower
  concurrency limit spreads the same repeated setup over more time instead of
  removing it; it is throwing hardware at it in reverse.
- **Guard a slow shape with a slow check.** A script that walks the tree for
  the shape after the fact is more cost; make the shape unwritable at its
  owner (step 10).
- **Pay for a measurement twice.** Read the recorded times before rerunning
  anything to time it. Never rerun a suite to see whether it got faster when
  the per-test record can say.
- **Answer "is it fast now" with a time measured before a change.** Read the
  current record, or measure once when none exists since the change. Until
  then the answer is "not measured since <change>", with no number beside it.
- **Report red herrings.** Leave each of these out entirely, even as a
  footnote, a caveat or "what I haven't measured":
  - machine load: other jobs, queue waits, busy disk or CPU, memory limits;
  - agent or model thinking time, reasoning effort, model choice;
  - how many agents there are, who relays messages to whom, the questions
    they ask, rules they did not follow, how many reviews a change gets;
  - failed checks or flaky tests as a cause of slowness (a failure is a bug to
    fix, not repeated work), unless the same failure came back after a fix;
  - time totals with no repeat in them ("an hour of building and testing",
    hours per category, a breakdown of the day);
  - outages and broken tools, and whoever fixed them;
  - work that justified its time (bugs caught, tests repaired);
  - plans and order: what lands next, who was told what.

  Fixing a bug or repairing a test once is the cost of doing business, never
  slowness: write that time off and report only the repeated work around it.
  A bug that comes back after its fix is repeated work, and it is reported.

  When everything you find is on this list, the answer is "no repeated work
  found", followed by what you checked.

## Prove each test

Run this for every test you write, keep, delete or judge, and before any
deletion in making it fast.

<what-to-do>
1. **Name the rule** the test is for, in one sentence: what must be true and
   at which entry point.
2. **Break the rule on purpose.** Run the stack's mutation-testing tool
   first (cosmic-ray or mutmut for Python, StrykerJS for JavaScript and
   TypeScript, cargo-mutants for Rust, PIT for Java, gremlins for Go): it
   breaks one site at a time and records which tests fail, so a test no break
   fails shows at once. A tool's break that fails several tests marks a
   suspect, never a duplicate. Then break the rule the test names by hand, in
   the smallest plausible wrong way: skip the request, return the default,
   swap the currency, drop the write, take the other branch. Also break what
   the test depends on, not just what it asserts: make the request never
   arrive, the file never open, the service unreachable.
3. **Run the tests of that module** and record which fail.
   - Nothing fails: the test cannot fail. Go to step 4.
   - Only this test fails: it is needed. Keep it.
   - This test and another fail: one is a duplicate. Keep the one at the
     public entry point against the real boundary, and delete the other.
4. **Fix a test that cannot fail at its cause.** The usual cause is in the
   code, not the test: several different failures collapse into one answer
   ("unavailable", `None`, an empty list, a generic error), so a test
   expecting that answer passes when the request never arrived. Give each
   failure its own variant carrying its facts (the status code, the missing
   field, the address that refused), and have each test assert its own
   variant. When the assertion is the problem (it checks a default the code
   returns anyway, a fake answers before the real path runs, it asserts a mock
   was called), assert the observable result only the correct path produces.
5. **Undo the break,** run the module's tests again, and confirm all pass.
6. **Before writing a new test,** do steps 1 to 3 for its rule against the
   existing tests first. Write it only when nothing else fails for the break.
   Names never show coverage by proxy: an end-to-end test that asserts the
   final price already checks the currency rule, though its name says
   "creates a product". Only a deliberate break shows it.
</what-to-do>

## What counts as repeated work

Judge inputs per **unit**: each test, package, module or file, never the
whole command. A command whose commit changed can still redo hundreds of units
whose own inputs did not, and "no command ran twice on identical code" proves
nothing about them.

- Tests and checks run on code the change did not touch: the whole
  workspace's tests for a change to one package, every test for a change to
  config or docs. A test's inputs are the code it exercises, not the commit.
- A build, compile or type check that redoes every file when one changed,
  because its cache key is coarser than its inputs.
- One program loaded several times for one change: a load per file checked,
  or a separate whole-program load per check where one load could serve all.
- A check whose findings another step already produces on the same change.
- Regenerating, reinstalling or rebuilding output whose inputs are unchanged.
- Serial steps that each rebuild what the step before them just built.
- A check that two stages both run, in either direction. Whichever stage runs
  more often is the redundant one. A push check that builds every artifact,
  installs from scratch or walks the whole product repeats what the release
  proves on its own build; those belong to the release alone. The push proves
  only what changed; the release proves the whole product once. A release that
  reruns a per-unit proof every push already made repeats it.
- The same work on the same commit in two places: the working checkout
  compiles and tests, then a gate's own folder compiles and tests that commit
  again because its cache is separate.

## Make it fast

<what-to-do>
1. **Record every test's own time, before touching a test.** Turn on the
   runner's per-test timing so each run writes it: `gotestsum --jsonfile` and
   `gotestsum tool slowest` for Go, the built-in test reporter for Node,
   `--durations=0` or a duration hook for pytest, `--reporter=json` for
   Vitest or Jest. Keep a history file, and make the runner itself read the
   recorded bar through its own hook (a pytest plugin hook, a Jest or Vitest
   reporter, a gotestsum post-run step), never a second runner written beside
   it, print every test over it and fail it; the full check fails
   the same way over its own limit. Time spent waiting on other machine work
   is subtracted, so the judge cannot fail on load. Whole-command wall clocks
   and prose ("the suite is slow") are never evidence.
2. **Prove each instrument can disagree** before reading a number from it:
   the script exists where you ran it, the output file is non-empty, the log
   is from a run that reached the step and finished, the redirect sends what
   you think it sends. Measure in the context the test really runs in (the
   same runner, wrapper and environment), or the fix's effect is hidden.
3. **Read the real steps and their caches.** Open every check entry point:
   package scripts, task definitions, hooks, the push gate, CI jobs, the
   release command and the build driver, including steps still being added
   and any step proposed as a fix. A new gate or hook is where repeated work
   enters, so it is audited like the rest, never named as the fix unaudited.
   For each step write down what it loads or builds, its inputs and its cache
   key, read from the code rather than guessed from names. Find where each
   step stores results and count the entries it wrote in the last day; each
   new entry is one rebuild.
4. **Trace three paths and compare every place.** Trace a recent real
   commit, the smallest change there is (one line of config or docs), and one
   release from start to finish. List every compile, build, test run and
   check each path ran, in order, with the folder and cache each ran in. Then
   write a table with one row per place work runs (working checkout, each
   hook, gate folder, push, CI, release, any copy) and one column per piece of
   work, and compare **every pair of rows**. Work that appears in two rows for
   the same inputs belongs only in the row that must run it. Everything the
   config-only change ran beyond checking that file is repeated work.
5. **Read what each slow test starts.** Most causes are visible in the code:
   a child process, an interpreter start, a browser, a database migration, a
   build, a sleep, a new connection per write. Read the hot path first, then
   profile once to confirm the cause you named, never to search for one. When
   reading does not show it, profile one trivial run of the smallest slow test
   (a CPU profile plus a count of processes started); a fixed per-step cost
   shows up there and dominates every test.
6. **Sweep every test file for the known causes,** not only the slow ones
   you have read: search the whole test tree for each cause in the table
   below. A hit marks a suspect; its cost comes from the per-test record from
   step 1, never from a new timing run. Rank the causes, and the repeats from
   step 4, by total cost: the number of runs or tests that pay it times what
   each pays. Fix the most expensive first. A small cost every test pays beats
   the slowest single test. The usual causes, each with its fix:

   | Cause | Fix |
   | --- | --- |
   | Script logic in a command file, so a test can only run it as a child process | The work is an exported function the test imports; the command file only parses arguments and prints |
   | A blocking child process per test | One non-blocking spawn helper, wiring tests run concurrently, one per command, and a check that refuses blocking spawn calls in tests |
   | A fixed sleep, or polling until a lock or lease clears | Wait for the event: the process exit, the written row, the listener accepting, the lock released |
   | A small program started for every lookup (version control, path resolution, file locks) on every step | Read those facts once per run, or in-process |
   | A new database connection, schema run or fsync per write | One prepared connection per thread, reused |
   | Setup built again in every test: migrations replayed, a scratch repository with fixture commits, a dependency tree copied into each fixture, a whole store copied in and out | Build it once from a template keyed by its inputs, only when no template with that key exists, under a lock so concurrent runs build it once; give each test a cheap copy |
   | A server or service (database, broker, browser, emulator) started per test file, per worker or per test | One per machine or run, started once by the runner's global setup; each file gets a copy inside it |
   | A fresh copy per test where a rolled-back transaction would isolate it | A transaction per test, rolled back; a test whose claim needs committed data uses a separately named helper |
   | Checks that fire only on commit (deferred constraints, commit hooks, triggers on commit), which a rolled-back test never reaches | The shared setup makes them fire right after each statement, so rollback tests still exercise them; the few tests that depend on commit timing keep their own copy |
   | Copies or servers left behind by killed runs | Name each by its owner process; at startup, remove those whose process is gone |
   | A test that runs on a large input to prove something a tiny one shows | Test on the smallest real input that can show the behaviour |
   | A browser, runtime or emulator booted per test or per lookup | One per run, a fresh context per test |
   | A cache keyed on a whole folder, or on more files than the tool reads, so a docs edit reruns everything | Key per unit, on exactly the inputs the tool reads, plus the toolchain |
   | A test moving the cache location | Pin the cache path at process start |
   | Rebuilding or reparsing unchanged input on every step | A content-keyed store shared by every step and checkout |
   | Compiling and linking when only compiling proves the claim | Compile only |
   | Code that multiplies compile work (generic wrappers instantiated per type, reflection that keeps every method alive) | Plain types at the hot boundary; typed dispatch |
   | A wrapper or launcher whose fixed startup cost every nested step pays again | Nested steps run inside their parent's process or session |
   | Native fixtures built per test | Built once per machine, keyed by their inputs |
   | A slow tool where a faster one enforces the same rules | Swap it, then prove each rule still fires (step 9) |
   | A transaction or resource with no cleanup on failure | A helper that registers the rollback or close as test cleanup, so a failure reports instead of hanging |
   | The same check in two stages, or a full suite for a change to one unit | Delete it from the stage that runs more often; run only the tests whose imports reach the changed files |
   | A test another test already catches | Delete it, once **Prove each test** shows the other fails for its break |

7. **Fix the cause at its owner,** once, for every test or run that has it:
   the shared helper, the fixture, the runner, the cache key, the build step,
   the check's own entry point. The fix changes the measured cause and nothing
   else: a new script, hook, service or check that measures or guards the slow
   thing is not a speed fix, and is built only when the user asks for it.
   - **First ask whether the step needs to exist.** When another step proves
     what it proves, earlier or later (a release that runs after the push
     counts), delete it from the stage that runs more often, together with any
     agent rule that requires it. Prove it with a break: breaking the rule
     must still fail the step that stays. "A bug could slip through" is not a
     reason to keep a step whose proof already exists. A stored result is only
     for a step that must stay.
   - **Remove work before spreading it.** Account for every unit of work the
     slow test or step still does (each process started, each file judged,
     each build, each boot) and remove each one that repeats: reuse a stored
     result keyed by everything it read, and build, load or start each thing
     once per process. When the product already stores such results, the
     test goes through that store rather than around it. Prove it: an
     unchanged rerun does zero units, and one changed input redoes exactly its
     own unit. Only then may the remaining, justified units run in parallel.
   - **Put each piece of setup at the widest scope its inputs allow,** and
     give each test the cheapest isolation that still proves its claim:

     | Scope | What lives there | Keyed by |
     | --- | --- | --- |
     | Machine | servers and services: a database, broker, browser, emulator, runtime | tool version and config |
     | Run | prepared state: migrated schema, seeded data, built fixtures | the files that make it |
     | File or worker | a cheap copy of the prepared state | its owner process |
     | Test | isolation inside that copy, undone at the end | nothing |

     Isolation, cheapest first: a transaction rolled back at the end; a copy
     of a template (a template database, a copy-on-write file or folder, a
     fresh browser context, a key prefix on a shared server); a fresh
     instance, only for a test whose claim needs one, through a separately
     named helper so the exception shows in the test.
   - **Put the fix inside a step agents already run** (the commit hook, the
     existing check command, the compile step), so nobody has to remember a
     new command. Prefer per-unit results keyed by contents, toolchain and the
     public interface of dependencies, shared by every caller and checkout. A
     stored result beats a background process; a prose rule or a new manual
     step is never the fix.
   - **A repeat that has been found is never paid again, by anyone.** The
     first commit is the smallest change that stops it, touching nothing that
     would set it off, and everything else waits for it. Stop a slow run in
     progress rather than wait it out. Before any commit, yours or another
     agent's, check it against the table from step 4: a change that touches
     every package sets off the most, and waits until the repeat it would set
     off is stopped. Tell everyone working in the repository what the repeat
     is and to hold changes that would set it off. A plan's time for a fix is
     the edit alone; a plan whose time includes a repeat pays it, so reorder
     it until no step does.
8. **Name what must invalidate each stored result:** toolchain, plugin or
   config versions; ambient or global types; dependents through other files;
   generated files; staged contents rather than the working folder; separate
   compilation projects. Say how the fix handles each.
9. **Prove the fix keeps its meaning.** Every test the fix touched still
   passes **Prove each test**. A swapped tool runs on the same files with the
   same rules; check it with a probe file that breaks each rule on purpose,
   because some tools silently ignore a rule name they do not know. A reused
   result is reused only when its inputs are unchanged **and** its last run
   passed; a failed or unknown result reruns. Delete only after searching
   every config for the deleted name. When setup moves to a wider scope,
   break isolation on purpose: one test writes, and the next test or file
   must not see it. If it does, the shared setup leaks and the fix is not
   done.
10. **Make it impossible to come back.** Make the slow shape unwritable at
    its owner, so no check is needed to catch it:
    - the shared helper or fixture is the only public way to get the
      resource; the call that starts a server, opens a fresh database or
      boots a browser is private to it, so a test cannot spell the slow
      shape;
    - the runner's configuration owns the scope (global setup starts the one
      server; per-file setup hands out copies), so a test file has nothing
      to configure;
    - the cheap path is the default and the exception has its own named
      helper, so choosing the expensive one shows in the test's code;
    - a procedure agents run step by step (landing a commit, releasing,
      rebuilding when the main branch moves) is one command the repository
      owns, and the fix changes that command. A rules file telling agents
      which steps to skip is a reminder, not a fix.

    Only when the owner cannot make the shape unwritable, add a rule to a
    linter or type checker the repository already runs on every change,
    never a new script that walks the tree. Then write the shape and its
    owner into the repository's agent rules (`AGENTS.md` or its equivalent)
    in the same commit as the fix.
11. **Make every checkout get it.** A speed-up that lands only on the
    development branch while other worktrees and branches keep the slow code
    is not done: every checkout gets it with no extra work from anyone.
12. **When several agents work in parallel,** give each shared or generated
    file exactly one writer, and put standing answers in the shared brief.
13. **Loop** to step 1 with the new record until nothing is over the bar and
    nothing repeats.
</what-to-do>

Done when every test written, kept, deleted or judged has its rule, its break
and the list of tests that failed for it; every step a change runs has its
inputs and cache key written down; the three paths are traced and every pair of
places compared; the per-test record shows every test and every check under
the bar; each fixed cause has its rule and, where possible, a check that
refuses it; each stored result has its invalidation list; and every checkout
has the fixes.

## When work lands slowly

When the user asks why work takes so long to land, from an issue to a pushed
commit or a feature the user can use, the answer is the repeated work on that
path. The red herrings above stay out of it.

1. **List the work** in the window the user names: the issues closed or still
   open and their commits. Read the history (`git log`, the issue timeline,
   reverts); never answer from memory.
2. **Trace each one** from issue to first commit, to push, to close, and mark
   every step that happened more than once:
   - a bug that came back: the same symptom in a second issue, a revert, a fix
     of a fix, the same failure seen again after a fix landed;
   - work redone: a brief or plan rewritten because it was wrong, a commit
     replaced, a change made and undone, a review finding what a rule already
     said;
   - a step rerun on the same input: the same gate or check run again with
     nothing changed.
3. **Find the step that let each one back in**: a test that does not catch the
   bug, a rule stated only in prose, a fix made at one instance instead of the
   owner, two owners of one fact, a brief that left the worker a choice.
4. **Fix that step** so the repeat cannot happen again, using
   `correct-by-construction` for a bug's class, then report.

Report one item per repeat, bullets only:

- **What repeated:** the issues and commits, each as a link with its title,
  and how many times it happened.
- **Why it came back:** the step that let it, with `file:line` or the rule.
- **Stop:** the fix, and the check or rule that keeps it from returning.

Then "Left:" with repeats not yet fixed, or "nothing". When nothing repeated,
the answer is "no repeated work found", followed by the work items checked.

## Report

Only when done, and in the time section of any status update, summary or
handoff. Bullets only.

One line per test proved:

- `test name`: rule; break used; tests that failed → kept, deleted (duplicate
  of `other test`), or fixed (what changed in code or assertion).

One item per slow cause or repeat:

- **Cause:** the shape or the step that repeats, with `file:line` of its
  owner, and how many tests or runs had it.
- **Before → after:** measured times, from the per-test record or the step's
  own timing. Write only numbers you read; anything else is "not measured".
  "Not measured" applies to a number, never to whether a step repeats.
- **Guard:** the deletion, the stored result and what it keys on, or the rule
  and the check that keeps the cause from returning.

Then two lines: the slowest test and the slowest check now, with their times;
and "Left after these fixes:" with the remaining repeated work, or "nothing".
Explain a technical term in a few words the first time it appears.

## Example

Wrong:

- Five translator tests pass even when their request never arrives, because a
  failed request gives the same answer they expect. (Reported, not fixed.)
- These five probably have other tests already; I can check if you like.
  (Asked instead of breaking the rule.)
- Here are the 12 slowest tests; the top one takes 8 s. Should I keep going?
  (A status table with the bar unmet.)
- `exports_report` is slow because the machine was busy. (A red herring, and
  unconfirmed.)
- 1.3 h waiting in the build queue, 1.0 h of building and testing. (Time
  totals with no repeat in them.)
- Split `imports_catalog` into three tests of 4.9 s each. (Faked; the slow
  import is still there.)
- `judges_all_fixtures` went from 46 s to 12 s by running its 66 fixtures as
  parallel subtests. (Same work on more cores; every fixture is still judged
  from scratch on every run although none changed.)
- I rewrote `renders_invoice` to skip its child process. (One test; the 40
  others that spawn the same command still do.)
- No findings for the strict-boolean rule. (The log was from a run that died
  before the linter started.)
- Deleted the gate's unit-test step because CI runs the same tests. (No break
  proof; CI ran a different test selection that missed the rule.)
- Kept `check_queries.py` because it catches broken SQL and no other check
  does. (Nothing opens that SQL; the check and the SQL both go.)
- Kept `check_route_ids.py` because it catches a renamed id. (The page and
  the test could import the id, so a rename fails the build; the check has
  nothing to catch.)
- No command ran twice on identical code, and the new push gate runs only one
  test run, so it is the fix. (Judged per command, not per test, and the gate
  named the fix unaudited: it ran all 299 tests on every push, 10 minutes for
  a config-only change.)

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

- **Cause:** 41 tests ran the CLI as a blocking child process, because its
  logic lived in the command file (`src/commands/export.ts:12`).
- **Before → after:** 9–14 s each → 0.2–0.8 s; the suite 6 min → 40 s.
- **Guard:** "Scripts and their tests" rule in `AGENTS.md`; a lint refuses
  `spawnSync` in test files.

- **Cause:** `judges_all_fixtures` judged all 66 fixtures from scratch on
  every run, bypassing the stored verdicts the product keys by what each
  judgement read (`tests/judge_fixtures_test.go:30`).
- **Before → after:** 46 s → 0.3 s unchanged (zero fixtures judged); one
  edited fixture re-judges only its own row, 0.4 s.
- **Guard:** "Tests go through the verdict store" rule in `AGENTS.md`; the
  test asserts an unchanged rerun starts zero judgements.

- **Cause:** the push gate compiles the whole workspace, builds both apps and
  walks the shop (`scripts/gate.sh:40`), all of which the release runs again.
- **Before → after:** not measured → the push runs format and the changed
  units' tests only.
- **Guard:** deleted from the gate after breaking the price rule failed the
  release's shop walk; the release keeps the full build.

- **Cause:** the compile cache is keyed on a hash of the whole source folder
  (`build/cache.ts:18`), so any edit rebuilds everything.
- **Before → after:** 124 full compiles in 12 hours, about 1.5 min each →
  one file's recompile per edit.
- **Guard:** the store is keyed per file by its contents, the toolchain and
  its imports' public types; the compile, type check and single-file check all
  read it.

Slowest test now: `migrates_orders`, 1.1 s. Slowest check: the full check,
7 s. Left after these fixes: nothing.
