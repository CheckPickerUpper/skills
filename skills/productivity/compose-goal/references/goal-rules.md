# Rules for the compose-goal skill

Composer-facing: this file is drafting guidance. Copy only the behavioral
contract and hard-blocker list into a goal. Never publish this rulebook as part
of the goal.

The goal is an execution contract, not a backlog export. It tells an agent what
a person must be able to do, how that behavior is owned, and what evidence will
prove it.

## Outcome before implementation

The first sentence names the human outcome. The paragraph beneath it explains
the current state, the failure it causes, and the state the goal creates.

Implementation details belong in the task, constraints, or boundaries. Issue
closure, deleted files, migrated languages, crate counts, screenshots, and
recordings are not outcomes.

A useful cold-read test is: can a person who has never opened the repository say
what they will be able to do when the goal is complete?

Example:

~~~text
BAD
# Agent Goal: Finish the API migration
Verified by: a browser recording shows signup, booking, deposits, and history;
rust-backend-walk.gif exists.

GOOD
# Agent Goal: Let an operator complete and review the full booking workflow in the product
When this is complete, an operator can sign up, invite staff, connect payments,
take a registration and booking deposit, schedule the balance, hold and release
a damage deposit, message a customer, store a file, and see who changed each
record and when.

The recording, if requested, is evidence of those real actions. It is not the
thing being built.
~~~

The good form makes a fake page visibly insufficient because the outcome is a
product capability, not a file or recording.

## One outcome and full scope

One goal carries one coherent human outcome. Keep every requested behavior that
belongs to that outcome. Do not rename a large task as a smaller migration or
split it into unrequested phases.

When issues are involved, check that every referenced issue contributes to the
same outcome. An implementation issue can belong when its change is required
for the outcome, but its role must be clear in the task or boundary. An
unrelated issue, a second user outcome, or a separate product decision needs a
separate goal or one focused user decision before publication.

The goal's completion test is whether the person can perform the outcome. A
goal that can be completed by closing issues or deleting files has lost the
product target.

## Issues are live references

Issue bodies are composer input and execution-time source material. Read each
full body while composing so the outcome and traceability are grounded in the
actual request. Record only the repository and issue reference in the published
goal:

~~~markdown
## Issues in scope

Repository: owner/repo

Read the current body of each issue before acting:

- owner/repo#123
- owner/repo#456
~~~

Do not paste issue bodies, copied acceptance criteria, or paraphrased issue
sections into the goal. That creates a second requirement store that grows the
gist, drifts from GitHub, and hides which issue owns each behavior.

At execution time, fetch the live body again. If the body has changed, use the
current text only when it still fits the goal outcome and boundaries. If it
changes the outcome, required surface, or verification contract, report the
issue number and the conflict before writing.

Issue state is bookkeeping. Closing an issue is not proof that the product
behavior works. The goal must name the command, request, or observable state
that proves each behavior.

## Traceability gate

Build a requirement-to-proof map before drafting:

| Human behavior | Source | In-scope implementation | Real proof |
| --- | --- | --- | --- |
| the person can complete ... | user request or repo#N | product/API/client/test path | command and output or observed state |

The map may stay in the composer's scratchpad. The published goal must still
make the outcome, boundaries, issue references, and proof surface explicit.

Every verification step must point to a behavior in the outcome. Every behavior
must point to a requirement source and an in-scope path that can make it true.

A screen, route, or browser flow missing today is valid only when the goal
includes the work that creates or repairs it. If the goal excludes that work,
the verification step is orphaned. Hold the goal before publication and ask one
focused question or report the exact missing scope.

A screenshot, video, GIF, fixture, or report is evidence only when it records
real product behavior. It becomes a deliverable only when the user explicitly
asks for that artifact as the outcome. A proof artifact cannot create a missing
screen, database row, payment, message, file, or history record.

For browser proof, each step must use the real product or API-backed application,
perform a real user action, and leave or reveal real state. A static page with
buttons that only update local display state proves only that the static page
works.

The executing agent should surface the relevant command output, API response,
database state, or browser result in the transcript. Silent success and file
existence alone are not enough when the claim is behavior.

## Evidence rules

Start with one line:

Verified by: <concrete evidence joined with AND>.

Each clause names:

- the behavior it proves;
- the command, request, or interaction that exercises it; and
- the output or state that counts.

Use live issue references for detailed acceptance criteria, but add the proof
surface. For example:

~~~text
Verified by: owner/repo#731's live acceptance criteria are met, with the real
checkout request returning the expected response and the end-to-end test
printing its passing summary.
~~~

Do not use these as sole gates:

- works as expected;
- looks good;
- tests pass without a runner and output;
- all issues are closed;
- a screenshot, recording, or GIF exists;
- a page contains the requested labels.

Join independent gates with AND. An AND gate is valid only when every clause
proves part of the same human outcome. Remove a clause that has no owner,
implementation path, or real proof.

When the work is testable, end the goal with the exact repository test
invocation. Discover it from the repository's scripts or instructions; do not
guess a runner. For docs, chores, and config, use a concrete file-content,
grep, or other runner-free check.

## Goal shape

Draft in this order:

1. # Agent Goal: <plain-language outcome title>
2. One short current-state paragraph.
3. The full task in imperative voice.
4. Verified by: <concrete, AND-joined evidence>.
5. ## Issues in scope, containing repository and issue references only.
6. ## Verification, with one bullet per command or interaction and the output
   that counts.
7. ## Constraints.
8. ## Boundaries, including the natural surface and an escape hatch for a
   shared dependency that needs to change.
9. ## Between iterations.
10. The behavioral contract below.
11. The hard-blocker list below.

The title and paragraph stay in plain product language. The task carries the
implementation detail. The issue section points at live ownership. The
verification section proves the outcome. Do not add drafting commentary,
backlog summaries, or copied issue bodies.

## Behavioral contract while pursuing this goal

1. Keep the human outcome as the target. Treat issue closure, implementation
   migrations, screenshots, recordings, fixtures, and file lists as means or
   supporting proof.
2. Prove real behavior. Drive the actual product, API, client, or test path and
   show output that establishes the resulting state. A visual artifact cannot
   substitute for missing product behavior.
3. Read every referenced issue live before implementation and verification. Use
   current issue text only when it still fits the outcome and boundaries.
4. Keep the full requested scope. When normal implementation work is difficult,
   inspect more code, find the owning path, and continue.
5. Surface transcript-visible proof for every verification clause. Show the
   command, request, interaction, and confirming output or state.
6. When a browser step lacks an in-scope real product path, report the exact
   orphan requirement instead of making a proof-only screen.
7. Continue until every outcome and proof gate is true. Do not add a turn or
   time limit.
8. Follow the target repository's instruction files. This goal does not
   override system, platform, or repository rules.
9. Stop only for a hard blocker from the list below or when the user says stop.

## Hard blockers

Hard blockers are the only reasons to stop short of the verification gate:

- Authentication failure that no command can recover, such as an expired token
  with no refresh path.
- Network unreachable for a required remote operation.
- Irrecoverable merge conflict in business logic that the agent cannot resolve.
- Build environment corrupted beyond recovery in the current session.
- A required behavior or verification clause has no implementation path inside
  the goal's boundaries, and adding that path would change the requested
  outcome or scope. Report the exact clause, the missing path, and the decision
  required.
- A live issue materially conflicts with the goal's outcome, boundaries, or
  verification contract and cannot be reconciled without user direction.
- The user explicitly says stop in a follow-up turn.

These are normal work, not blockers:

- Hook, lint, type, or test failures. Fix the implementation or the test's
  wrong invariant and continue.
- A large issue set or a long implementation.
- A missing screen when the goal explicitly includes building the screen.
- A long live issue body. Read it; do not copy it into the goal.
- An artifact that has not yet been produced when it is only supporting proof.
- Uncertainty about an implementation path. Read more code and find the owner.
