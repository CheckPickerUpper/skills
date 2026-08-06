---
name: stacked-prs
description: "Stacked pull requests: build, restack, and land a chain of dependent PRs so each layer reviews as one focused change. Use when opening work that sits on top of an open PR, when a base branch moves under a stack, when the stack tool reports an invalid base or refuses to insert a PR, or when a stacked PR's diff shows changes it does not own."
---

# Stacked pull requests

A stack is a chain of branches where each layer's base is the layer beneath it, so reviewers read one focused change at a time and the chain lands in order. Layered work opened as loose branches all targeting trunk hides that order, and whoever lands them has to reconstruct it from base refs.

## Relabel is not restack

The one thing agents get wrong. Two separate things have to be true:

- **Relabel** — the PR's base on the host points at the branch below. This is metadata.
- **Restack** — the branch's commits actually sit on top of that branch. This is history.

Stack tooling relabels. Only `git rebase` restacks. A stack that is relabelled but not restacked looks correct in the UI, and its merge will conflict, because layer N never contained layer N-1's commits.

Relabel-only is invisible on inspection: the host computes a PR's diff from the merge-base, so each PR still renders its own changes and nothing looks wrong. Restack, then relabel.

## Build or update a stack

1. **Fetch, and trust the remote over your local ref.** `git fetch origin --prune`, then read the truth with `git ls-remote origin <ref>`. A stale remote-tracking ref sends the whole rebase onto the wrong base, and the damage only surfaces as conflicts several steps later.

2. **Restack bottom-up.** Rebase each layer onto the branch below it, starting from the one nearest trunk. A layer rebased onto a base that is itself about to be rebased is work you will redo.

3. **Repoint anything that names a rewritten commit.** A rebase rewrites every SHA it replays. Files that record commit hashes — approval ledgers, changelogs, provenance records — go stale on the spot, and a gate reading them fails on a branch that passed moments earlier. Fix them in the same rebase.

4. **Validate a structured file before staging it.** When a conflict lands in JSON, YAML, or TOML, parse it and let the parse fail loudly before `git add`. A resolution script that throws mid-way leaves conflict markers on disk, and staging blind commits them.

5. **Push each layer with an explicit lease.** `--force-with-lease` needs the expected value spelled out (`--force-with-lease=<ref>:<sha>`) whenever the local branch name differs from the remote one; the bare form has no remote-tracking ref to compare against and refuses with stale-info.

6. **Relabel last**, once every layer's history is real.

Run the stack tool's own `--help` for its current subcommands. It is in public preview and the surface moves, so what it reports beats what any document remembers.

## Done when every layer contains the one below

The check, for each adjacent pair:

```
git merge-base --is-ancestor <lower-branch> <upper-branch>
```

True for every pair means the stack is real. One false means that layer is relabelled only. Run this before relabelling and again after, on every pair — a stack is only as sound as its weakest link, so a spot-check of one pair proves nothing.

Then confirm each PR's changed-file count and diff size match what that layer alone owns.

## Traps

| Symptom | Cause | Move |
|---|---|---|
| Tool rejects the base as invalid, or refuses a PR | It only appends to the top of an existing stack | Remove the stack grouping and relink the full chain in order; the PRs survive |
| A layer's gate fails right after a clean rebase | Rewritten SHAs stale a file that names them | Repoint to the new SHA, then rerun the gate |
| The same file conflicts on every stacked change | An append-only list is a single serialization point | Resolve by keeping every side's entry; raise splitting the file if it keeps recurring |
| Rebase lands on unexpected commits | Local remote-tracking ref was behind | `git fetch --prune`, verify with `git ls-remote`, redo |
| Push refused with stale info | Lease had no remote-tracking ref to compare | Pass the expected SHA explicitly |

## Land it

A stack merges in order from the bottom. Each layer still faces branch protection and required checks, so stacking never skips a gate.

When a layer's own history carries records that a squash would orphan — commits referenced by hash from a file in the tree — land that layer as a merge commit so those commits stay reachable from trunk. Verify after merging: `git merge-base --is-ancestor <recorded-sha> origin/<trunk>`.
