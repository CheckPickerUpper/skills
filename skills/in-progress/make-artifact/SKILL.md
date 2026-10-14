---
name: make-artifact
description: "Make, revise, or republish a claude.ai Artifact of any kind: report, audit, decision page, dashboard, tracker, form, tool, game, diagram, deck, or doc. Triggers: 'make an artifact', 'publish this as a page', 'turn this into an artifact', 'build a dashboard', 'update the artifact', and every revision after the reader says a page is too long, too thin, too technical, or not something they can act on. Owns the reader's job, sourced facts, information density, revision without overcorrection, and the publish loop. The page contract stays with quickstart, artifact-design, and artifact-capabilities."
short_description: Make and revise Artifacts that do their reader's job.
clients: [claude]
allow_implicit_invocation: true
---

# Make an Artifact

This skill owns what goes on the page and the loop around publishing it. The
page contract (format, title, tokens, themes, libraries, storage, size) belongs
to the Artifact tool's `quickstart`, `artifact-design`, and
`artifact-capabilities`. Follow them as the authority and use this skill for
everything they leave to judgment.

## 1. Name the job

<what-to-do>
Before writing a file, write one sentence: "<reader> opens this to <job>."
Pick the job from the table. It sets the first screen and where records live.

| Job | First screen shows | Below it | Records live in |
|---|---|---|---|
| Decide | the choice being made and the recommendation | each option: what it costs, what it unblocks, its evidence | page source |
| Plan (spec, port, migration, roadmap) | what is missing: each gap between today and the goal, stated as a fact and grouped by what it stops | the build order as numbered steps, each ending in something the reader can try; then the decisions the reader owns; acceptance detail last | page source |
| Understand (report, audit, explainer, diagram) | the answer or finding in one sentence | one scannable unit per item, then detail | page source |
| Monitor (dashboard) | current state and what needs attention now | trends and breakdowns | live data or the `db` capability |
| Record (tracker, form, checklist, sign-up) | the action control and the current records | history | the `db` capability |
| Use (tool, app, game) | the working interaction, on first load | help and settings | a capability; browser storage only for per-viewer conveniences |
| Present (deck, doc, design) | what the quickstart type prescribes | what the quickstart type prescribes | the type's own store |

Then settle two things the sentence leaves open:

- **Scope.** Say whether the page covers every member of something ("every
  ability step") or one case of it ("the Hora ability"). When the reader names
  a kind of thing, the rows are all of its members, read from where they are
  declared, and a single case appears only as a labelled example. State on the
  page what the scope leaves out.
- **Reading constraints.** Write down anything the reader said about how they
  need to read it: tired, deciding fast, "no extraneous load", "without reading
  code", "show me the code". These hold for every version of the page, not only
  the next one.

Done when the sentence, the scope and the reading constraints exist, and the
draft's first screen answers the sentence without scrolling.
</what-to-do>

## 2. Settle the facts first

<what-to-do>
- Source every claim from something read in this session: a file, command
  output, issue, query result, or doc. Put the source beside the claim as a link
  the reader can open.
- Measure numbers rather than estimating them. State how a number was counted
  when the method is not obvious.
- Before presenting a question or option as open, search for an existing
  answer: issue threads, decision records, sibling repositories, and the user's
  earlier messages. Present a question that is already settled as the decision,
  with its source.
- Put a decision in front of the reader only when they raised it or the work
  cannot proceed without it. Whether to do the thing they asked for is not a
  decision to hand back.
- State the premises the page depends on near the top, each with its source:
  the plan it assumes, the design that replaced an older one. A reader who
  cannot find the premise assumes the author missed it.
- Read the underlying records (issues, rows, logs, files) before choosing how
  the page is organized. Group them, and let the grouping that explains the
  most records set the headline and the sections.

Done when every claim carries a source, every question on the page is one the
reader raised or the work needs and survived a search for its answer, and the
page's organization came from the records.
</what-to-do>

<supporting-info>
A polished page makes an unsourced claim look settled, so errors travel further
than they would in chat. A page that asks the reader to decide something they
already decided gets corrected and costs their trust in the rest of it. A
structure picked before reading the records answers the author's guess; the
real headline often sits in the records' text, such as a run of issues that all
say the same screen is broken.
</supporting-info>

## 3. Write in layers

<what-to-do>
Build every page in three layers:

1. **Answer**: the job's answer from step 1, in plain words, on the first screen.
2. **Items**: one scannable unit each, built as below.
3. **Detail**: what is left once every item has its claim, its evidence and its
   consequence, behind a disclosure (`<details>`, a tab, a drill-down, or a
   link out).

Each item carries five things, all visible without opening anything:

| Part | What it is | Wrong shape |
|---|---|---|
| Claim | a heading that states the fact and names the thing: "`ReadBody()` returns an object that includes the methods that kill the body" | a metaphor or teaser the reader has to decode: "Anything that can read a body can also end it" |
| Evidence | what lets the reader check the claim themselves: the numbers, or the real lines with file path and line number | a paraphrase that asks to be trusted |
| Consequence | one concrete case of what goes wrong because of it, and what the fix makes impossible | a claim that leaves the reader asking "OK, and?" |
| Status | when the item mixes states (today or planned, built or not built), which state each fact is in | a small label on some facts, or two states in one unmarked list |
| Source | a link to where it came from | none |

Rules for the parts:

- **Every line is one the reader uses.** Cut reassurance ("nothing is broken
  today"), restatement, and the author's opinion of the work's importance.
- **A plain name leads and the exact name sits directly beneath it.** Plain
  words say what a thing does; the code name, signature, issue number, command
  or path stays visible under them, exactly as written. Hiding the exact names
  loses the reader who verifies; leading with them loses the reader who does
  not read code.
- **Code is shown as code.** Copy the real lines, mark the lines the claim
  rests on, put a short note beside each marked line, and show the lines after
  the fix. Colour the syntax. Give inline code names in a sentence or heading
  their own colour and background in both themes, so they stand out from the
  words around them.
- **One encoding for status, on every view.** Pick one visual treatment per
  state (solid box for today, dashed for planned; a chip per build state), put
  its legend at the top, and use it in every tab, table and drawing.
- **Draw it when the subject is what happens where or when.** Steps that move
  between machines, people or phases are a diagram or a timeline, drawn with
  `make-diagram`. A table of thirty rows that each open with a code name is a
  reference appendix; it goes in the detail layer under the drawing.
- Replace each figurative or coined phrase with the fact it stands for: "thin
  coverage" becomes "3 of 11 endpoints have tests".
- **References support a claim; they never stand in for one.** A row whose
  content is `FS:170-185` tells the reader nothing. Write what those lines do,
  then cite them by their real path (`Shared/FrostStomp.ts:170-185`) as a link
  or with the lines shown. Use no abbreviation or internal code (`FS`, `T2`,
  `Q14`) the page does not spell out where it is used.

Done when a reader of the first screen alone can do the job, every item's
claim can be checked from what is visible beside it, and no heading needs
interpreting.
</what-to-do>

<supporting-info>
Plain-words-only pages fail the reader they were simplified for: with the code
removed, the reader cannot see the scope or validate the claim, and has to
trust the author. Simple means the claim is stated literally and the proof is
laid beside it, with nothing else on the page competing for attention.
</supporting-info>

See [references/density.md](references/density.md) for one page drawn four
ways (overloaded, gutted, vague, layered) and
[references/item.md](references/item.md) for one code finding drawn as bare
prose and as a full item.

## 4. Publish

<what-to-do>
For a new artifact:

1. Call the Artifact tool with `action: "quickstart"` and the fitting `intent`.
   Follow the type or skill it names. Load `artifact-capabilities` before
   writing any runtime behavior.
2. Write the file in the session scratchpad.
3. Before every publish, re-read the whole file. Read each CSS declaration in
   the token and theme blocks as a value, and check each link target.
4. Take the one pre-publish look `artifact-design` allows whenever the page
   draws anything to scale or has layout you wrote by hand (breakpoints, bars,
   grids). Spend it on those parts.
5. Run the page check and fix what it prints until it exits 0:

   ```bash
   python3 <folder of this SKILL.md>/scripts/check_page.py <page.html>
   ```

6. Publish with `icon` set to one generic word. Pass it on a path's first
   publish only; a redeploy carries no icon field.

To update, republish the same file path. For an artifact from another
conversation, `read` its URL first, build on what comes back, and publish with
`url`.

A watch-ended notice saying the artifact was not found, or a publish reporting
it deleted or access lost, means the link is dead. Tell the user in that turn,
then treat the next publish as a new artifact without `url`.

Reply with the link and one or two lines saying what the page answers. The page
carries the content.

A question whose answer depends on the page waits until the reader has seen
it. When they say they cannot open or see it (another device, a phone), send
the relevant view as a rendered image in that turn.
</what-to-do>

<supporting-info>
The browser drops an invalid CSS declaration without a sound, so a garbled
token beside a valid one renders fine until the order flips, and nothing in the
publish path reports it. Proportional drawings and hand-written breakpoints are
the parts a reader sees wrong first and the author never sees at all.
</supporting-info>

## 5. Revise from feedback

<what-to-do>
1. Keep a **keep-list**: everything the previous version showed, everything the
   reader asked for across all their messages, and the reading constraints
   from step 1. Every item on it survives every revision, including a rebuild
   from scratch.
2. Place the complaint on one axis and change that axis alone:

   | Reader says | Axis | Change |
   |---|---|---|
   | too much, can't scan, overload | density | move detail down a layer; cut lines the reader does not use |
   | too technical, not consumable, I have to read code | vocabulary | plain names lead; exact names stay visible beneath them |
   | missing, lost context, where did X go | coverage | restore it from the previous version |
   | vague, can't decide from this, abstract | concreteness | swap phrases for measured facts and source links |
   | where's the code, I just have to trust you | evidence | put the real lines, numbers or records beside the claim |
   | OK and?, so what, why is this bad | consequence | add the concrete case of harm and what the fix makes impossible |
   | why the metaphor, what does this mean | wording | restate the heading as the literal fact, naming the thing |
   | stop tying it to X, show all of them, shouldn't it show Y too | scope | return to step 1's scope and re-enumerate from the source |
   | which of this exists, what's today and what's planned | status | one encoding per state, with a legend, on every view |
   | never asked that, extraneous | relevance | remove it, and remove every other line of the same kind |
   | doesn't say what's missing, what's the order | plan shape | rebuild to step 1's Plan row: the gaps first, then the numbered order |
   | what is this reference, what does this code mean | references | write the fact; cite it by full path, shown or linked |
   | wrong, outdated | accuracy | return to step 2 |

3. Apply the change to every item of the same kind. A comment anchored on one
   heading is a report about all the headings.
4. When the reader cannot say which form would work, build the candidate forms
   from the real content as tabs on one page and let them pick by looking.
5. Check the revision against the published version and fix what it prints
   until it exits 0. It lists links, issue references, code names, column
   headings and repeated labels (such as status chips) that the last version
   showed and this one does not; each is restored or given a reason in the
   file the output names:

   ```bash
   python3 <folder of this SKILL.md>/scripts/check_page.py <page.html> --previous <last published.html>
   ```

   Save the published file as `<page>.published.html` after each publish so
   the next revision has it to compare against.

Done when the complaint's axis moved on every item it applies to, the check
exits 0, and nothing else left the page.
</what-to-do>

<supporting-info>
The common revision failure is a pendulum: "too much" gets read as "delete",
the reader objects to the lost content, and the restore comes back as abstract
phrases that carry no facts. Each swing loses information the reader needed.
Density is a question of which layer content sits in, so it is fixed by moving
content between layers. A rebuild is the riskiest revision: reorganizing the
rows around a new idea quietly drops a whole column, such as the built or not
built marker on every cell, that nobody asked to remove.
</supporting-info>
