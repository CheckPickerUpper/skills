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
| Understand (report, audit, explainer, diagram) | the answer or finding in one sentence | one scannable unit per item, then detail | page source |
| Monitor (dashboard) | current state and what needs attention now | trends and breakdowns | live data or the `db` capability |
| Record (tracker, form, checklist, sign-up) | the action control and the current records | history | the `db` capability |
| Use (tool, app, game) | the working interaction, on first load | help and settings | a capability; browser storage only for per-viewer conveniences |
| Present (deck, doc, design) | what the quickstart type prescribes | what the quickstart type prescribes | the type's own store |

Done when the sentence exists and the draft's first screen answers it without
scrolling.
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
- Read the underlying records (issues, rows, logs, files) before choosing how
  the page is organized. Group them, and let the grouping that explains the
  most records set the headline and the sections.

Done when every claim carries a source, every open question survived a search
for its answer, and the page's organization came from the records.
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
2. **Items**: one scannable unit each: a name, the one or two numbers that
   matter, one plain sentence of state, and a link to the source.
3. **Detail**: everything else, behind a disclosure (`<details>`, a tab, a
   drill-down, or a link out).

Write in concrete nouns and the reader's own vocabulary. Replace each
figurative or coined phrase with the fact it stands for: "thin coverage"
becomes "3 of 11 endpoints have tests". Keep the terms the reader must act on
exactly as they are: issue numbers, commands, names, paths.

Done when a reader of the first screen alone can do the job, and a reader who
wants proof reaches any source in one click.
</what-to-do>

See [references/density.md](references/density.md) for one page drawn four
ways: overloaded, gutted, vague, and layered.

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
5. Publish with `icon` set to one generic word. Pass it on a path's first
   publish only; a redeploy carries no icon field.

To update, republish the same file path. For an artifact from another
conversation, `read` its URL first, build on what comes back, and publish with
`url`.

A watch-ended notice saying the artifact was not found, or a publish reporting
it deleted or access lost, means the link is dead. Tell the user in that turn,
then treat the next publish as a new artifact without `url`.

Reply with the link and one or two lines saying what the page answers. The page
carries the content.
</what-to-do>

<supporting-info>
The browser drops an invalid CSS declaration without a sound, so a garbled
token beside a valid one renders fine until the order flips, and nothing in the
publish path reports it. Proportional drawings and hand-written breakpoints are
the parts a reader sees wrong first and the author never sees at all.
</supporting-info>

## 5. Revise from feedback

<what-to-do>
1. Keep a **keep-list**: every piece of content the reader asked for, across
   all their messages. Every item on it survives every revision.
2. Place the complaint on one axis and change that axis alone:

   | Reader says | Axis | Change |
   |---|---|---|
   | too much, can't scan, overload | density | move detail down a layer |
   | too technical | vocabulary | reader's words on top; technical terms move to detail |
   | missing, lost context, where did X go | coverage | restore it from the previous version |
   | vague, can't decide from this, abstract | concreteness | swap phrases for measured facts and source links |
   | wrong, outdated | accuracy | return to step 2 |

3. Diff the new file against the published version. For each removed line,
   name the layer it moved to or the message where the reader asked for it gone.

Done when the complaint's axis moved, every keep-list item is present, and no
other content left the page.
</what-to-do>

<supporting-info>
The common revision failure is a pendulum: "too much" gets read as "delete",
the reader objects to the lost content, and the restore comes back as abstract
phrases that carry no facts. Each swing loses information the reader needed.
Density is a question of which layer content sits in, so it is fixed by moving
content between layers.
</supporting-info>
