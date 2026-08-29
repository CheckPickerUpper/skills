---
name: to-issues-clearly
description: "Create GitHub issues from a plan, bug, finding, audit or PRD, whose titles a stranger can act on. Use when filing issues or turning work into issue-sized slices. Builds every title as what somebody wrote or did followed by what the system did with it, refuses words that exist only inside the codebase, and reads each title cold before publishing. Splits issues by whether anything visibly breaks; cuts vertically and sizes each to one fresh context window; sequences a wide refactor as expand-migrate-contract; puts the breakdown to the user before publishing anything; and wires real GitHub sub-issue edges rather than prose references."
---

# To issues clearly

Turn a plan, bug report, audit finding, or PRD into live GitHub issues that explain the outcome clearly enough for another person to implement and verify.

The tracker is the publication surface. Draft in the conversation, then create or edit the issue directly with GitHub. The skill supplies judgment and a repeatable shape; GitHub supplies the issue number, labels, and relationships.

## The title is the whole job

Everything else here is ordinary. This part is not, because it fails constantly and always looks fine at the time.

### The shape

**A title has two halves: what somebody wrote, asked for, or did — then what the system did with it.**

    A config can set retries to five, and the client gives up after three
    A user can mark an invoice paid, and the balance does not move
    A migration can declare a rollback, and it is never run
    A CLI flag can ask for JSON, and it prints a table

The first half does the work. It forces you to name something a real person actually does, and you cannot write it about a mechanism, because mechanisms are not written by anyone. Most bad titles die right there — there is nothing to put in the first half.

When nobody wrote anything and the thing simply misbehaves, the first half is the action that sets it off:

    Deleting the last admin leaves the account with no owner
    Retrying a failed upload uploads it twice

Not a state of affairs, and not a description of code. Something a person does, then what came of it.

### Every word must survive a stranger

**A word that exists only inside your codebase costs the reader a lookup. Two of them and the title is unreadable, however plain each one looks on its own.**

`rule`, `tag`, `arm`, `node`, `handler`, `resolver`, `context`, `entry`, `record` are all concrete nouns and all internal. Replace each with the thing it stands for in the world the software is about — an invoice, a retry, a login, a status.

This is the one that is easiest to think you passed. Read only the title, and for each noun ask: would somebody who has never opened this repository *know* what it refers to? Not "could they guess". Know.

### The output check

**Write the title with your rule, then read it cold and answer: what is broken?**

If the honest reaction is *ok, and?*, it has failed — even when it breaks none of the rules below. This is what catches the titles that read fine while the reasoning is still in your head.

These four shipped from an earlier run of this skill, and every one of them passes every ban in the next section:

    A cosmetic's access route is the only fact its availability needs
    Adding a tag to a fighter actually adds it
    A formula reads from the caster or the target as part of what it is
    Suppressing a tag either works or cannot be declared

Not one has a first half. Not one survives "and?". A ban list cannot catch these, because banning is a way of saying what not to write, and there is always an infinite amount left over. The shape is what closes it.

### The backstop

The shape and the stranger test catch most of it. These constructions still get through, so they are refused outright:

| Never write | Why it fails |
|---|---|
| "…actually does X" | Sarcasm. Scoring a point instead of naming a defect. |
| "…as part of what it is" | Type vocabulary in a domain costume. Says nothing. |
| "X is the only fact Y needs" | A conclusion from reasoning the reader did not hear. |
| "X either works or cannot be declared" | Two outcomes joined by an invisible rule. |
| "X is an answer a caller can act on" | Abstract. Name the answer and who is stuck without it. |
| "X forgets / remembers / knows Y" | Code personified. Code does not forget. |

**No bare abstract noun as the subject.** "Availability states the same fact four times" — availability of *what*? Name something the reader can picture.

**No word with two readings in the domain.** "An author can contradict it" — a person writing content, or an in-world author? If it can be misread, replace it.

**A type defect still takes the shape.** Do not name the type in the title and do not paraphrase it away either. Say what somebody can write and what becomes of it; name the type in the first line of the body, where the implementer needs it and nobody else has to read it.

### Worked corrections

These come from one game codebase. The shape does not.

    A cosmetic's access route is the only fact its availability needs
      -> An item can say it is a drop and unselectable at the same time

    Adding a tag to a fighter actually adds it
      -> Dying does not mark a fighter dead

    A formula reads from the caster or the target as part of what it is
      -> A formula can say it reads from the caster, and the game throws
         that away and decides again

    Suppressing a tag either works or cannot be declared
      -> An effect can declare "keep this status off them" and the game
         ignores it

    An error and a warning reach the output differently
      -> Code can report an error, and it prints exactly like a warning

The last one is worth studying: it described the *desired* state as though it were the defect. A title names what is wrong now. What you want instead belongs in **Desired outcome**.

### The good sentence is usually already written

When a title fights you, look at how you described the issue in prose — in the conversation, in the Problem section, in a commit message. That sentence is usually already in the shape, because explaining something to a person forces both halves out of you. Prefer it over anything composed against this section.


## Process

### 1. Gather the target

Identify the repository and the source material. Read an existing issue, plan, or evidence file when one is supplied. Explore the codebase only when the issue needs a fact the conversation does not establish.

Search existing issues for a duplicate before creating anything. **Read the candidates rather than matching on words** — an issue asking for the opposite change is not a duplicate, it is the reason this one exists, and the new issue should reference it.

Reuse an existing issue when it already represents the same outcome; update it when the user asked to reshape it.

### 2. Decide which kind of issue each one is

Ask this before writing any title, because it decides what goes in the first half of the shape:

**Does anything visibly break?**

- **Yes** → the first half is the action that sets it off. `Retrying a failed upload uploads it twice.`
- **No** → the first half is what somebody can wrongly write. `A config can set retries to five, and the client gives up after three.`

Never write a behaviour title for a problem with no behaviour. That is where invented poetry comes from: you reach for a user-facing sentence, there isn't one, and you produce something that sounds like a sentence but names nothing.

An issue whose only symptom is "the type permits nonsense" is a real issue. Say so plainly and stop.

### 3. Shape the issue set — err on granular

One issue per outcome that can be implemented, reviewed, and closed on its own.

**When in doubt, split.** Two issues that turn out to be one merge in seconds. One issue that turns out to be four is discovered halfway through implementing it, by somebody who now has a half-finished branch and no way to land any of it. The costs are not symmetrical, so the tie goes to splitting.

**Count the acceptance criteria — that is the granularity check.** Four to six is an issue. More than eight is a system wearing an issue's clothes, and the split is usually already visible: each cluster of criteria that could be built and reviewed alone is its own issue.

Split when two outcomes could land separately, when two parts would be reviewed by different people, or when one part could ship while the other waits on a decision. Keep observations together only when they share one end state and one review.

**Cut each issue vertically, not by layer.** One issue is a narrow but complete path through everything it touches — the shape, the code that reads it, the callers, the tests. An issue that is only the schema change, with the callers in a second issue, cannot be verified or landed on its own.

**Size each one to a single fresh context window.** Someone picks it up knowing nothing about today's conversation. If finishing it needs more than they can hold at once, it is two issues.

**Look for the prefactor and file it first.** *Make the change easy, then make the easy change.* When one preparatory change would make three others straightforward, that is its own issue and it blocks them. Finding it after filing the three is finding it too late.

Use words a maintainer would recognise. Keep file paths and proposed APIs out of the title unless the user has already made that decision.

### 3a. The wide refactor is the exception to vertical slicing

A **wide refactor** is one mechanical change — rename a field, retype a shared symbol, split a union — whose blast radius fans across the whole codebase. A single edit breaks hundreds of call sites at once, so no vertical slice can land green and forcing one produces an issue nobody can finish.

Sequence it **expand → migrate → contract**, as separate issues:

1. **Expand.** Add the new form beside the old. Nothing breaks, because everything still uses the old one. This issue lands green on its own.
2. **Migrate**, in batches sized by blast radius — per package, per directory, per feature. **Each batch is its own issue, blocked by the expand.** CI stays green batch to batch because the old form still exists.
3. **Contract.** Delete the old form once no caller remains. One issue, **blocked by every migrate batch.**

When even a batch cannot stay green alone, keep the sequence but let the batches share an integration branch, and have them all block a final integrate-and-verify issue. Green is promised only there — say so in that issue rather than implying each batch is independently green.

Spot one by asking: *would doing this in one commit break call sites in files this issue does not name?* If yes, it is a wide refactor, whatever it looks like.

If the breakdown is obvious, publish it without ceremony. Ask one focused question only when an unresolved choice changes the issue count, scope, or relationship tree.

### 4. Write the body

~~~markdown
## Problem

What is wrong, who hits it, and what it costs them.

## Desired outcome

What should be true when this is done.

## Acceptance criteria

- [ ] Something observable that shows it is done.
- [ ] The failure, boundary or empty case, when there is one.
- [ ] The old bad state is no longer reachable through the supported path.

## Evidence

Only for a defect that exists now: where it is, and the quoted code that proves it.
~~~

The plainness rule governs the body too. It is a report, not a case being argued.

**Every criterion is something you can watch happen.** Someone must be able to close the issue by doing the thing and seeing the result — not by reading the diff and agreeing with it.

| Checkable | Not checkable |
|---|---|
| A fighter killed by the death effect reads as holding the dead tag | Add tag handling |
| An item marked drop-only and unselectable no longer compiles | Make availability a proper union |
| Buying a second hour while one is running ends four hours from now, not two | Fix the extend logic |

Three rules that catch most bad criteria:

- **No criterion names a file, class, or function.** If it does, it is describing the implementation somebody has not chosen yet.
- **One criterion, one observation.** A criterion with "and" in it is two criteria, and half of it will be skipped.
- **Include the failure and the empty case.** "The old bad state is unreachable" is the criterion that stops an issue closing while the defect still has a back door.

**Keep file paths out of everything except Evidence.** A path in the Problem or the criteria is a guess about code that does not exist yet, and it rots between filing and implementing. Describe the behaviour and let the implementer find the file.

Evidence is the one exception, and only when the issue asserts something is broken **right now**. A claim nobody can check is worse than a path that might move, so a finding cites where it is and quotes the code that proves it. Say which commit or day it was read on — Evidence is a snapshot, not a live pointer.

An issue describing work that does not exist yet has no Evidence section at all. It has nothing to cite.

### 5. Put the breakdown to the user before publishing anything

**Nothing is created until the user has seen the set.** An issue published wrong has to be edited, and a set published wrong has to be edited eleven times.

Show a numbered list. For each: **title**, **blocked by**, and **what it delivers** in one line. Then ask three things:

- Is the granularity right — too coarse, too fine?
- Is each blocking edge real, or is it just ordering?
- Should any of these be merged or split?

Iterate until they approve. Read the titles back to yourself here too (step 8) — before publishing is when it is cheap.

Skip this only when the user has already approved a breakdown in the conversation, or asked explicitly for a single issue.

### 6. Publish, blockers first

Create issues in dependency order — anything that blocks something else goes first — so a child can reference a real number instead of a placeholder.

~~~sh
gh issue create --repo OWNER/REPO --title "..." --body-file ISSUE_BODY.md --label LABEL
~~~

Apply the tracker's agent-pickup label (commonly `ready-for-agent`) unless told otherwise. These issues are written to be picked up cold; that is what the label says.

Read the repository's existing labels first and use them. **Never invent a label.** If none fits, publish without it and report the gap — the user decides whether a new label exists.

`gh issue create` takes repeated `--label` flags. Building them in a shell loop is where they silently go missing; `read -ra` is not portable to zsh. Verify the labels landed afterwards rather than assuming.

For an existing issue, edit it and preserve its history. Do not create a second issue because the wording changed.

### 7. Wire relationships natively — prose is not a link

**Writing "Part of #189" in the body does not create a relationship.** It creates a sentence. The tracker still shows an orphan, no board groups it, no query finds it, and closing the parent does not surface the child. Every relationship you state must exist as a native GitHub edge.

So: if you write it in prose, you must also create the edge. If you cannot create the edge, say so in the report — never let a prose reference stand in for one and call the tree wired.

Create the edge after both issues exist, using the issue database id:

~~~sh
# sub-issue (parent -> child)
gh api repos/OWNER/REPO/issues/PARENT/sub_issues -F sub_issue_id=$(gh api repos/OWNER/REPO/issues/CHILD --jq .id)
~~~

Note `-F`, not `-f`. `-f` sends the id as a string and the API rejects it as not an integer.

A blocker is genuine only when the child cannot start, or cannot meet its criteria, until the blocker lands. Ordinary sequencing is not a blocker, and "related" is not a parent.

**Never close or edit a parent issue.** Wiring a child under it does not give you licence to touch it. If the parent's own text is wrong, say so in the report and let the user decide.

**Verify every edge by reading it back**, not by trusting the create call:

~~~sh
gh api repos/OWNER/REPO/issues/PARENT/sub_issues --jq '.[] | "\(.number) \(.title)"'
~~~

If an edge cannot be created, report the URL and the missing edge rather than implying the tree is complete.

### 8. Read your own titles back

Before reporting, list every title with no other context — no body, no conversation, no repository open — and put each through both checks:

1. **The shape.** Point at the first half and the second half. If you cannot point at a first half, the title is about a mechanism and has to be rewritten around whoever wrote or did something.
2. **The output check.** Answer *what is broken?* If the honest reaction is *ok, and?*, it fails, however many rules it obeys.

Then read every noun once more and ask which of them exist only inside this repository. Two is unreadable. One is a lookup you should have spent somewhere else.

Any title that fails gets rewritten and the issue edited before you report. This step is where the bad ones get caught — they always read fine while the reasoning is still in your head.

## Final report

Report the issue URLs, the labels that actually landed, the edges that actually exist, and any unresolved publication step. Name the gaps rather than implying completeness.
