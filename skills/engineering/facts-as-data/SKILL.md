---
name: facts-as-data
description: "Move knowledge buried in logic into one table every reader shares, before a second copy exists. Use when sweeping a codebase for hard-coded name lists, regex alternations of names, branches that differ only in data or append-lists every change edits; when designing that table and the check that fails on a missing case; when reviewing whether a diff's next case is one new row; and when deciding whether code should become data at all."
short_description: "Turn facts buried in logic into one checked table."
allow_implicit_invocation: true
metadata:
  when: "the same list is copied in code"
  situation: Writing code
---

# Facts as data

<what-to-do>
A fact is **buried** when it lives only inside logic: a list of names inside one handler or rule, a regex alternation of callee names, match arms whose bodies differ only in a literal, a list every change appends to. A buried fact has one reader. The second reader writes a second copy, and the copies drift. Move the fact into a **table** every reader shares, with a **completeness check** that fails the build when a case is missing.

The skill has three moves. A census leads into design; a review of one diff stands alone.

## Census

1. Run `python3 <skill-folder>/scripts/buried_facts.py <paths>`. It lists **leads**: names joined in a regex alternation or an `||` chain, literal lists of names, and runs of branches keyed by a literal; its `--help` gives the thresholds. It skips test files unless given `--include-tests`. A lead is a place to read; whether the fact is buried is your judgment.
2. Read the code for the buried facts no pattern shows: branches whose bodies differ only in a constant, two functions that differ only in a name, and a shared append-list (registry, module list, schema list, chained command) that every change edits.
3. Group the leads by what they mean, in domain words: "calls that pause the thread", "retry libraries", not the rule or file that holds them. A meaning found at two sites already has two owners; name both sites in its group: one of them must become the owner and the other read from it.
4. Record one row per lead site in a census file, in the format in `references/census-format.md`: `table` (it moves into a table), `is-table` (it already is the shared table) or `not-data` (its variation has no real form; see the counter-test below). Rerun with `--record <census.tsv>` until it exits 0. Keep the census in the issue body or the task's decision log.

The census is done when the script exits 0 against the record and every group names its meaning.

## Design

For each group recorded as `table`:

1. **Key.** Name what readers look the fact up by, as the question they ask: `role_of(language, name) -> role`.
2. **Storage that merges.** One file per entry, or one entry per line in sorted order, registered by the build (a build script, a generated index, directory discovery). Two changes that each add an entry touch different files or different lines. A hand-appended shared list is the shape this skill removes.
3. **Readers.** Name every logic site that reads the table. Each private copy is deleted in the change that moves its reader onto the table.
4. **Completeness check.** Add the build or test step that fails, naming the missing case, when an entry a reader needs is absent: a language with no entry for a role a compiled rule reads, an enum case with no row. Its own test removes one entry and expects the failure to name it. A table with no completeness check is the same list in a new place.

**Counter-test, as strong as the main rule.** Code stays code when its variation has no real form. Apply the no-invented-axes test: name the axis of variation in one line, using cases that exist now. When the line cannot be written (one case, fields nobody varies, a config DSL or data file built to express a single branch), record the group as `not-data` with that reason and leave the logic as it is.

Design is done when every `table` group names its key, storage, readers and completeness check, and every `not-data` group names its reason.

## Review of one diff

1. Run `python3 <skill-folder>/scripts/buried_facts.py --since <base> <paths>`. It reads only the lines the diff adds.
2. For each lead, and for each new case the diff handles, ask: **can the next case be added as a row with no edit to logic?**
   - Yes: the change is declarative; report it clean.
   - No, and a table for this meaning exists: the diff wrote a second owner around it. The finding is to add the case to that table.
   - No, and no table exists: the finding names the table the fact belongs in, its key and its completeness check.
3. A lead stays in the logic only when the counter-test holds; quote its one-line reason in the review.
</what-to-do>

<supporting-info>
## Why tables

- **Rule of representation** (Unix): fold knowledge into data so program logic can be stupid and robust.
- **Policy and mechanism separate**: the table is policy, the logic that reads it is mechanism, and each changes for its own reasons.
- **Open/closed**: a new case is a new row; the logic stays closed.

The payoff is in two places. Data can be checked as a whole: completeness, order and duplicates in one pass, where facts in logic are checked one branch at a time. And additions merge: entries in their own files or sorted lines do not collide, where two appends to one list always do.

## Boundaries

- A fact that already has two owners is a drift problem: pick one owner and make the other read from it.
- A bug is fixed by making its class of bad state impossible to write.
- This skill catches the first buried fact, before the second copy exists and before any bug.

## Worked example

A census of a code checker's rules found about 30 lists of what library functions do (which calls pause, run a program, read the environment, talk to a database, raise a failure) inside about 25 rule and matcher files. Seven facts were written twice word for word. A polling-loop rule held the pause functions in a regex, `(?:time\.sleep|sleep|asyncio\.sleep)`; a retry rule held its own retry libraries and `name.contains("sleep") || name.contains("backoff") || name.contains("delay")`. A function missing from one list was missed by that rule alone, and adding a language meant finding every list by hand.

The design became one function-role catalogue: keyed by language, name and role (`role_of(language, name) -> role`), one file per language and role, one sorted entry per line, registered by a build script the way rules are. Rules ask for a role; each private list is deleted when its role moves. The build fails when a supported language has no entry for a role a compiled rule reads. The first piece moved the pause functions.
</supporting-info>
