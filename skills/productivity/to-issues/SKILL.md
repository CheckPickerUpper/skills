---
name: to-issues
description: "Break a plan, spec, or PRD into independently-grabbable issues using tracer-bullet vertical slices, then wire the blocked-by/parent relationships into native GitHub sub-issues and dependencies so the tracker renders the real tree (not just prose). Use when converting a plan into issues, creating implementation tickets, or breaking work into slices."
---

# /to-issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets), and leave behind a real dependency tree on the tracker, not prose that claims one.

> An improvement on Matt Pocock's [`to-issues`](https://github.com/mattpocock/skills). Same tracer-bullet slicing and issue template; the addition is a mandatory final step that wires the blocked-by/parent edges into native GitHub sub-issues and dependencies, so the tracker renders the real tree instead of leaving "Blocked by #N" as dead prose.

The issue tracker and triage label vocabulary should have been provided to you. If not, set them up before publishing.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Publish the issues to the issue tracker

For each approved slice, publish a new issue to the issue tracker. Use the issue body template below. These issues are considered ready for AFK agents, so publish them with the correct triage label unless instructed otherwise.

Publish issues in dependency order (blockers first) so every genuine blocker already exists when you wire the native links in step 6.

<issue-template>
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it here and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

For a genuine hard block — the slice cannot start, or cannot meet its acceptance criteria, until the blocker merges — write one line naming the WHY (the semantic a graph edge can't carry). Otherwise omit this section; the native links (step 6) carry the dependency itself.

</issue-template>

### 6. Wire native relationships (ALWAYS — this is the point)

After publishing, encode every relationship as a native link so the tracker renders the real tree — the sub-issue panel on the issue page, the hierarchy in Projects/roadmap — and tools can traverse it. Native links carry the relationships; build them every run. Two rules decide which edge to draw:

- **Add a blocked-by edge for a genuine block:** the slice cannot start, or cannot pass its acceptance criteria, until the blocker merges.
- **Add a sub-issue edge for containment:** the slice lives under its parent. Reach for blocked-by only when the child is genuinely gated on the parent.

On GitHub, the `gh` CLI gained `--parent` / `--blocked-by` / `--blocking` in v2.94.0 (2026-06-10). On older `gh`, use `gh api`. Both need the issue's database id, not its number:

```sh
gh api repos/{owner}/{repo}/issues/{N} --jq .id
```

A slice that lives under a parent slice in the same repo is a sub-issue. Build the tree parent-by-parent (each issue has at most one parent):

```sh
gh api -X POST repos/{owner}/{repo}/issues/{PARENT}/sub_issues -F sub_issue_id={CHILD_DB_ID}
```

A blocked-by edge that is not a single-parent hierarchy, or that crosses repositories, is a dependency. This is the only way to encode a cross-repo blocker, since sub-issues are same-repo only:

```sh
gh api -X POST repos/{owner}/{repo}/issues/{N}/dependencies/blocked_by -F issue_id={BLOCKER_DB_ID}
```

Verify before reporting done: `gh api repos/{owner}/{repo}/issues/{ROOT} --jq .sub_issues_summary` shows the expected child total, and `.../dependencies/blocked_by` lists each blocker. If a relationship did not take, say so; do not report a tree you did not build.

Do NOT close or modify any parent issue.
