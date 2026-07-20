---
name: readonly
description: "User-invoked modifier for evidence-first read-only investigation. Use when the user appends /readonly to a question or another skill request: answer by checking the codebase and available read-only sources, do not implement, do not open issues, do not mutate local or remote state, and do not guess with 'likely' or 'probably' when evidence can be gathered."
disable-model-invocation: true
---

# /readonly

Prove, don't guess. Investigate with every read-only source that can answer the question, then stop before changing anything.

This is a user-invoked modifier. Use it when the user explicitly writes `/readonly`, including beside another skill name.

## Core rule

When `/readonly` is present, treat every other instruction or invoked skill as diagnostic only. Run its reading, tracing, classification, and reasoning steps, but skip any step that edits files, opens issues, changes configuration, creates branches, commits, pushes, posts comments, deploys, installs, regenerates, or otherwise mutates local or remote state.

## Procedure

1. **Freeze the state.** Record `git status --short` and the current branch before investigating. Existing dirty files are user state; do not normalize, revert, stage, or explain them away.
2. **Find the answer in the repo first.** Read code, docs, tests, scripts, generated descriptors, config, git history, issues, and PRs as needed. Use fast search before narrow reads.
3. **Trace to the owner.** If the question is about a bug, behavior, design, or class-level problem, keep following writers, callers, schemas, generators, or specs until the codebase proves where the answer lives.
4. **Plan from evidence.** If the question asks what to do next, read the repo state, active branch, recent commits, open PRs or issues when available, failing checks if readable, and local planning docs before recommending work.
5. **Avoid unsupported language.** Do not answer with `likely`, `probably`, `seems`, `I think`, or estimate language for a codebase-answerable fact. Use `proved`, `not found`, or `unknown after checking`.
6. **Ask only after legwork.** Do not ask clarifying questions until the available evidence cannot decide between materially different meanings. When asking, state what was checked and what exact missing fact blocks the answer.
7. **Stop before action.** Recommendations may be concrete, but do not implement them, create tracking issues, update docs, run generators, or perform cleanup.
8. **Prove no mutation.** Before the final answer, run `git status --short` again. If anything changed during investigation, identify it and do not hide it.

## Read-only sources

Allowed:

- Repository reads: `rg`, `find`, `ls`, `sed`, `nl`, `cat`, `git status`, `git diff`, `git show`, `git log`, `git blame`.
- Read-only project commands that do not write files, caches, snapshots, lockfiles, generated code, databases, or external state.
- Read-only remote queries such as `gh issue view`, `gh issue list`, `gh pr view`, documentation pages, package metadata, or API GET requests.
- Browser or web research when the answer depends on current external facts.

Banned:

- File edits, `apply_patch`, redirects that write files, formatters, generators, installers, migrations, cleanup scripts, and commands that update lockfiles or caches in the repo.
- `git add`, `git commit`, `git checkout`, `git switch`, `git reset`, `git rebase`, `git merge`, `git push`, branch creation, stash mutation, or tag mutation.
- Issue, PR, comment, label, project-board, reminder, deployment, secret, or environment changes.
- "Tiny" implementation, quick fixes, doc touch-ups, or drive-by cleanup.

If the only proof requires mutation, do not perform it. Say what command or change would prove the answer and why it is outside `/readonly`.

## Combined skills

When `/readonly` is combined with another skill, `/readonly` overrides its mutation steps:

- `/fix-the-class /readonly`: locate the writer, name the bad state, identify the invariant owner, reject lower patches, and propose the protective change. Do not make the owner protective or add tests.
- `/antimatter-code-quality-review /readonly`: perform the review and report findings. Do not patch findings.
- `/to-issues /readonly`: shape the issue plan if asked. Do not create issues.
- `/dog-food-it /readonly`: collect existing evidence only. Do not run proof commands that mutate state.

## Output

Answer in this shape:

1. **Answer:** the direct answer, decision, or recommendation.
2. **Evidence:** the files, commands, docs, issues, or history entries that prove it.
3. **Checked:** the search/read path, especially when the answer is negative.
4. **Unknowns:** only facts that remained unknowable after checking, plus the exact evidence that would settle them.
5. **No-mutation proof:** final `git status --short` result, summarized without dumping unrelated user changes.

If the answer is "we do not know," the report must make clear that the codebase was checked and the uncertainty is real, not a guess.
