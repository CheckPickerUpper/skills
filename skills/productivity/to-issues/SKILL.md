---
name: to-issues
description: "Create high-level GitHub issues from a plan, bug, finding, or PRD. Use when filing issues or turning work into issue-sized slices; shape observable acceptance criteria and publish directly with GitHub."
---

# To issues

Turn a plan, bug report, audit finding, or PRD into live GitHub issues that explain the outcome clearly enough for another person to implement and verify.

The tracker is the publication surface. Draft in the conversation, then create or edit the issue directly with GitHub. The skill supplies judgment and a repeatable shape; GitHub supplies the issue number, labels, and relationships.

## Process

### 1. Gather the target

Identify the repository and the source material. Read an existing issue, plan, or evidence file when one is supplied. Explore the codebase only when the issue needs a fact that the conversation does not establish.

Search the repository's existing issues for a likely duplicate before creating a new one. Reuse an existing issue when it already represents the same outcome; update it when the user asked to reshape it.

Completion criterion: the target repository, issue count, and source facts are known.

### 2. Shape the issue set

Make each issue one independently understandable outcome. Split when two outcomes can be implemented, reviewed, or closed separately. Keep related observations together when they share one desired end state.

Use domain language a customer, operator, or maintainer would recognize. Keep implementation choices, file paths, class names, and proposed APIs out of the title and main problem statement unless the user has already made that decision.

If the requested breakdown is obvious, publish it without a planning ceremony. Ask one focused question only when an unresolved choice changes the issue count, scope, or relationship tree.

Completion criterion: every issue has one outcome, a bounded scope, and an identified relationship set.

### 3. Write the issue

Use this body shape:

~~~markdown
## Problem

What is wrong, who experiences it, and what consequence does it have?

## Desired outcome

Describe the high-level behavior or state that should exist when the issue is complete.

## Acceptance criteria

- [ ] An observable behavior demonstrates the desired outcome.
- [ ] The relevant failure, boundary, or empty state is handled when applicable.
- [ ] The old bad state is no longer reachable through the supported path.

## Evidence

Links, screenshots, logs, reproduction steps, or source references that justify the issue.
~~~

Acceptance criteria are finite, observable, and independently checkable. Prefer behavior over implementation: “a failed catalog request renders a recovery state” is useful; “add a try/catch” is not.

Use a short Parent or Blocked by section only when the relationship needs human context in addition to the native GitHub edge. A blocker is genuine when the child cannot start or cannot meet its acceptance criteria until the blocker lands.

Completion criterion: the title states the outcome, the body contains the problem and desired outcome, every criterion is observable, and evidence is traceable.

### 4. Publish directly

Create the issue with the authenticated GitHub identity:

~~~sh
gh issue create --repo OWNER/REPO --title "..." --body-file ISSUE_BODY.md --label LABEL
~~~

Use an existing repository label when one fits. If the requested label is absent, report that fact and continue only when the user has authorized creating labels.

For an existing issue, use GitHub's normal issue edit surface and preserve its useful history. Do not create a second issue merely because the wording changed.

### 5. Wire and verify relationships

When a parent or genuine blocker exists, create the native GitHub relationship after the issue exists. Prefer the current gh relationship flags; use the GitHub API when the installed CLI does not expose the needed operation. Use the issue database id for API relationship calls.

Do not encode ordinary sequencing as a blocker. Do not use a parent edge when the issue is merely related.

Verify each requested relationship on GitHub after creating it. If a relationship cannot be created, report the issue URL and the missing edge instead of implying that the tree is complete.

Completion criterion: every created issue has a URL and number, the requested labels are present, and every requested native relationship is confirmed or explicitly reported as unavailable.

## Final report

Report the created or updated issue URLs, labels, parent/blocker edges, and any unresolved publication step. The report is the completion proof; the issue tracker is the durable record.
