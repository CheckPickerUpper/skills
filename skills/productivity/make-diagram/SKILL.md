---
name: make-diagram
description: "Draw or revise any diagram for a reader: system map, flowchart, pipeline, process map, decision flow, architecture. Use whenever a diagram goes into an Artifact, doc, issue, PR or repository, and on every revision after the owner corrects one. Settles the domain and the plain words before drawing, puts rulebooks in tables, shows the mechanism as nodes, diamonds and lanes in a fixed SVG vocabulary, and ships a checker that renders light and dark images and refuses overlaps, small text, crammed boxes, comma lists, vague \"and\" rows, checks with no real example, steps drawn twice, dead ends, floating nodes, unlabelled branches, backward or crossing arrows, wrong arrow colours and captions."
short_description: "Draw diagrams a stranger can read, rendered and checked before delivery."
allow_implicit_invocation: true
---

# Make a diagram

A diagram shows a stranger a mechanism they would otherwise assemble from
prose: what comes in, what checks it, where each path goes. This skill owns the
drawing. On an Artifact page, `make-artifact` owns the page around it and
`artifact-diagramming` owns the inline-SVG mechanics (viewBox sizing, markers,
a self-contained `<svg>`). Where they differ, this skill wins: text is 15px or
larger, and the figure carries no caption.

## 1. Settle the domain

<what-to-do>
- List every node you mean to draw beside the source of its fact: the owner's
  words, a file, an issue, a page. A node with no source is a guess.
- Ask the owner when a flow is ambiguous (which source settles it, what happens
  when a check fails, who pays), using the client's question tool where it has
  one. Specifics come only from a source: no trial lengths, sample sizes,
  prices or timings that nobody gave you.
- Use the domain's real names. Codenames, placeholders and names the owner
  calls undecided stay off the drawing.
- Write words a stranger understands, naming what the thing does: "copy
  official stats", "sportsbooks", "what settles it", in place of internal terms
  such as "import feed facts", "operators", "deciding source".
- Read every noun and label cold, before the first render, as someone outside
  the business who is not technical. Each word is plain or defined on the
  page. Coined labels ("round", "keeper stat"), storage and tool names
  ("R2 games") and figures of speech ("each game entered twice") become what
  they mean: "our 27 games kept in full 4K", "two VAs score the same game".
  The system's own nouns (markers, tracks, crops, queues, verified records,
  rule checks) become the real thing a person sees: "the time Q2 starts",
  "the clip of the jumper".
- Record each replacement, yours from the cold read and every one the owner
  makes, in `<diagram>.words.txt` beside the diagram, one per line as
  `old phrase => plain phrase`, with an empty right side for a dropped name.
  The checker refuses the old phrase from then on, and refuses a diagram with
  no words file, so the cold read happens before the owner sees it.
- Leave no gap a reader has to ask about. Every check states its exact
  condition: a number, and what counts ("watched 90% of live play", not
  "enough watched"). Every branch says what happens next. Every end says
  whether it can be retried or left, and when ("can reapply after 3 months",
  not "Not admitted"). A rule nobody has decided shows the default you
  propose, marked "proposed"; vague words never stand in for it.
- Choose the form before drawing. A diagram is for flow between actors and
  steps. Levels, ranks and any states where each one has "move up when" and
  "drop when" conditions are a rulebook: a table with the columns state, what
  it means, when you move up and when you drop. A drawing of a rulebook needs
  arrows back to earlier states, which is the sign to use the table.
- For anything sold, the value is nodes: what it tells or gives the buyer, who
  pays, and why they pay. Name it concretely; a vague value undersells it.

Done when every planned node has a source, the owner has answered every
ambiguity, every check, branch and end has its exact rule, rulebooks are
tables, and the words file holds every replacement from the cold read and
the owner.
</what-to-do>

## 2. Plan the graph

<what-to-do>
Write the nodes and edges as a list before placing any coordinate.

- **An arrow means "waits on".** Draw A → B only when B cannot start until A
  is done. Outputs one step produces independently branch out from it side
  by side; chaining them ("time per game" → "accuracy per stat" → "clips")
  says each waits on the last. Ask of every edge: does the target really
  wait on the source?
- **Mechanism as nodes.** A box is a short title plus at most two short lines.
  A box that wants a paragraph is several steps; make each one a node.
- **Specific, not vague; specific is not a paragraph.** When a step is a list
  of concrete things a person does, the box is a titled checklist: the title,
  short subheadings ending in ":", and one "• " bullet per concrete thing.
  "VA marks the game" holds "Times:" • tip-off • each quarter's start and end
  • game end, "Teams:" • both team names • which team is home • each team's
  jersey colour • the referees' jersey colour, and "Court:" • which gym • 6
  points on the court lines • where the scoreboard is. Never a catch-all such
  as "jerseys and the court", which could mean a million things.
- **One item per row.** Two or more items are bullet rows ("• tip-off",
  "• game end"), never a comma list, and never two things joined by "and"
  with no specifics.
- **Concrete examples inside nodes.** "LeBron 2 pts in Q1 AND a turnaround
  jumper in Q4" shows what a field list ("player, stat, period") only names.
- **Every check is a diamond** with a labelled yes branch and a labelled no
  branch, and the no branch leads somewhere real: a refund, a retry, a
  rejection. The question names the object of the check: "the clip or official
  stat that settles the bet, found before the review deadline?", not "proof?".
  The diamond or its failure box shows a real case of what fails it, as a row
  starting "e.g.": "Each time after the one before?" with "e.g. Q2 starts
  before Q1 ends", not "Markers in order?" with "Back to the VA with the exact
  reason".
- **Lanes hold only what differs.** Official stats used as-is and AI-derived
  facts proven by rule checks are two lanes, with arrows showing exactly which
  part touches what. Where the lanes reach a step both do, they merge into one
  shared flow, and each shared step is drawn once below them. A step that
  differs by lane is a decision in the shared flow ("Brodie game?"), not a
  copy in each lane.
- **Related inputs share one bubble**: all sources in one group, with one
  arrow out of it.
- **Every node connects to where it comes from.** A downstream product gets an
  arrow from the checkpoint that enables it. An order or any other list joins
  the flow as nodes or stays off the drawing.

Done when every edge is written as "B waits on A because …", no node is
without an edge, no check is without a labelled no branch, no step appears
twice, no two sources of truth share a box, every check has its "e.g.", and
no box is over three short rows unless it is a titled checklist.
</what-to-do>

## 3. Draw in the vocabulary

<what-to-do>
Start from [references/example.svg](references/example.svg) and keep its
vocabulary, which the checker reads:

| Element | Markup |
|---|---|
| Box | `<g class="node">` holding one shape and its `<text>` rows |
| Decision | `<g class="decision">` holding one `<polygon>` diamond and its question |
| Group or lane | `<g class="group">` holding one shape and a title, drawn around its nodes |
| Arrow | `<path>`, `<line>` or `<polyline>` with `class="arrow <kind>"` and a `marker-end` |
| Arrow label | a bare `<text>` beside its arrow, clear of the line |
| Legend | `<g class="legend">`: one sample arrow and a one-to-three-word label per kind used |

Arrow kinds and colours: `yes` green, `no` red, `data` blue, `loop` amber and
dashed, `next` (a plain next step) grey. Only loop arrows are dashed, and yes
and no arrows leave a decision.

- **Direction.** Rows read left to right and wrap like text to the next row;
  sections stack top to bottom. Only a real loop, such as retraining or a
  retry, goes back.
- **Themes.** Node fills are pastel in both themes with dark text on them.
  Text on the background (lane titles, arrow labels, the legend) takes the
  theme's foreground. Inline in an Artifact, colours come from the page's
  tokens; a standalone `.svg` carries a `<style>` with a
  `prefers-color-scheme: dark` block, as the example does.
- **Size.** Text is 15px or larger where it is drawn. Place shapes on a grid
  with even gaps.
- **The drawing carries everything.** The `aria-label` states the one-sentence
  claim, and nothing sits under the diagram: no caption, footnote, "what
  changed" list or note. When a note seems needed, the drawing is missing a
  node or a label; add that instead.

Done when the file uses only the vocabulary above and every planned node and
edge from step 2 is in it.
</what-to-do>

## 4. Render, check and look

<what-to-do>
1. Run the checker on the `.svg` or on the `.html` page that holds it:

   ```bash
   uv run <folder of this SKILL.md>/scripts/check_diagram.py <diagram.svg | page.html>
   ```

   It renders each diagram in the light and the dark theme, writes
   `<stem>.light.png` and `<stem>.dark.png` beside the file (or in `--out`),
   prints each finding under the rule it breaks, and exits 1 while any remain.
   Fix the drawing and rerun until it exits 0.

   Three rules are judgment calls, marked "Judgment" in the output: a row over
   32 characters, two arrows that cross, and a non-loop arrow that points up
   or back. Some layouts are clearer with one of these, such as two lanes
   that both have to reach the same end box. Leave it standing only when
   moving it would make the drawing harder to read. An arrow back to an
   earlier level or state is never accepted: it is a rulebook, so make the
   table from step 1. Then add a line to
   `<stem>.accepted.txt` reading `<finding as printed> | <why>`; the owner can
   read your reasons there. Every other finding gets fixed.
2. Open both images and look at them. The checker measures geometry; your eyes
   judge the rest: the path reads in order, each label points at the arrow it
   names, nothing is cramped, and the mechanism matches step 1's sources. Fix
   what you see and return to 1.
3. Deliver the diagram. A reader who cannot open the page gets the PNGs.

Done when the last run exits 0 and you have looked at the light and dark
images that run produced.
</what-to-do>

<supporting-info>
Hand-placed coordinates look right in the source and wrong on screen: a label
lands on its arrow, a row spills out of its box, an arrow runs through a box
it does not connect. The author who never renders never sees it; the owner
sees it first.
</supporting-info>

## 5. Revise from corrections

<what-to-do>
- When the owner says they commented, read every comment where they left it
  (on an Artifact, the `ArtifactComments` tool's `read` action; on a PR or a
  doc, its review comments) and act on every thread. Answer each thread with
  what changed.
- A correction is about every element of its kind. A reworded term means
  searching the whole drawing for terms of the same kind; a moved arrow means
  checking every arrow of that kind. Add each wording correction to the words
  file.
- Keep what the owner already accepted; change what the correction names.
- Run step 4 again.

Done when every thread has an answer, the words file holds every correction,
and step 4 is done on the revised file.
</what-to-do>
