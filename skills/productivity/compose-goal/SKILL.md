---
name: compose-goal
description: "Compose or retrieve a gist-backed agent goal from a task or GitHub issues. Use when handing work to another agent and require a human outcome, live issue references, real behavior proof, and an explicit hard-blocker contract."
user-invocable: true
argument-hint: "<task description, or issue numbers like #111 #112>"
short_description: "Compose or retrieve a verified agent goal."
allow_implicit_invocation: true
---

# Compose Goal

Compose one executable goal from a task, or pull and run an existing goal
capsule.

When the request is to pull a goal rather than compose one, read
references/pull-goal.md and follow that branch. The pulled goal remains the
source of its outcome, verification, and hard-blocker contract.

<what-to-do>
## Compose branch

### 0. Resolve ambiguity with the user

Before drafting or publishing, apply this gate:

- In Claude, when any material ambiguity remains, use the `AskUserQuestion`
  tool to ask focused questions about the human outcome, scope, target
  repository, or proof. Wait for the answers before drafting or publishing.
- In every other agent, when a material ambiguity remains, ask one to three
  focused questions. Ask them together when possible, and wait for the answers
  before drafting or publishing.
- When no material ambiguity remains, continue without asking a question.

Do not ask a ceremonial question or use a plain-text question in Claude when
`AskUserQuestion` is available. Never invent an answer to pass this gate.

Completion criterion: every material ambiguity is resolved, and any required
user answers have been received.

### 1. Load the drafting contract

Read references/goal-rules.md before drafting.

Read the target repository's instruction files and inspect the commands that
define its test, build, and verification surfaces. Follow those instructions
when composing or publishing the goal.

When the request names GitHub issues, resolve the owner and repository, then
read every issue's current full body with:

~~~bash
gh issue view <number> --repo <owner/repo> --json number,title,state,body
~~~

Use the issue bodies as composer input. The published goal records the
repository and issue references, not copied issue bodies or copied acceptance
criteria.

Completion criterion: the user request, target repository, relevant
instructions, live issue bodies, and available proof surfaces are identified.

### 2. Establish the outcome

Write the human outcome before listing implementation work. State what a person
can do when the goal is complete, what must be true in the product, and why it
matters.

Treat crate counts, file migrations, deleted languages, closed issues, and
proof files as means or evidence. They may constrain or verify the work, but
they cannot replace the outcome.

Keep one goal to one coherent human outcome. If the requested issue set
contains separate outcomes, resolve that split before publishing instead of
flattening unrelated work into one goal.

Completion criterion: the outcome can be read without opening the repository,
and every requested behavior has a place in that outcome.

### 3. Run the traceability gate

For every behavior named in the outcome, privately map four things:

- the source of the requirement: the user's request or a live issue reference;
- the implementation surface that is in scope to make it true;
- the real product, API, client, or test state that proves it; and
- the output the executing agent must show in the transcript.

A verification step is traceable only when all four are present. A browser
screen, route, or workflow may be absent today when the goal explicitly
includes building it. A proof-only screen is never an implementation surface.

When a required verification step names behavior outside the goal's boundaries,
ask one focused question or report the exact orphan requirement before
publishing. Do not fill the gap with a fake page, state-changing buttons that
touch no product state, a screenshot, a recording, or a file whose existence
only proves that the artifact was made.

Completion criterion: every outcome behavior and verification step has one
requirement source, one in-scope implementation path, and one real proof
surface, or the goal is held for the user's decision.

### 4. Draft the goal

Use the exact structure in references/goal-rules.md.

The top of the goal contains the human outcome and its short current-state
paragraph. The task is imperative and preserves the full requested scope.
Verification describes real behavior and transcript-visible output. Screenshots,
videos, and GIFs are supporting evidence unless the user explicitly requested
the artifact itself as the outcome.

For issue-sourced work, use this shape:

~~~markdown
## Issues in scope

Repository: <owner/repo>

Read each issue's live body before changing files or verifying the result:

- <owner/repo>#<number>
- <owner/repo>#<number>
~~~

Do not paste issue bodies into the goal. The issue number is the reference and
the live issue is the source of its detailed acceptance criteria. Never make
"all issues are closed" the only verification.

Completion criterion: the draft has one human outcome, live issue references
where applicable, real behavior proof, and the behavioral contract plus
hard-blocker list from references/goal-rules.md.

### 5. Publish the goal

Write the full goal to a scratchpad file named goal.md outside the target
repository, then create a private gist. Secret is the default, so pass no
visibility flag:

~~~bash
gh gist create <scratchpad-dir>/goal.md --desc "agent goal: <title>"
~~~

The final output line is the gist URL. Keep the filename goal.md. To revise an
existing goal, edit the same gist and keep that filename.

Completion criterion: the gist exists and its goal.md contains the exact draft
that passed the traceability gate.

### 6. Copy and verify the handoff

Write only the short pull directive beside goal.md. It must start with /goal,
include the verification sentence, and contain no trailing newline.

~~~bash
printf '%s' "/goal Pull the agent goal from <gist-url> through compose-goal's pull branch, read it, and complete it exactly as written. Done when <verification sentence>; paste each verification command's output into the transcript as proof. Keep working until every verification line is true. Stop only on a hard blocker or if I say stop." > <scratchpad-dir>/directive.txt
wl-copy < <scratchpad-dir>/directive.txt
wl-paste > <scratchpad-dir>/directive-readback.txt
cmp -- <scratchpad-dir>/directive.txt <scratchpad-dir>/directive-readback.txt
~~~

If gist publication or clipboard readback fails, surface the exact error and
stop. Do not paste the full goal into chat as a fallback.

Completion criterion: the readback matches directive.txt byte for byte and the
directive starts with /goal.

### 7. Report

Report one line naming the gist URL and the copied directive length. Tell the
user to paste with Ctrl+V.

Completion criterion: the handoff report is the only user-facing output of the
compose branch.
</what-to-do>
