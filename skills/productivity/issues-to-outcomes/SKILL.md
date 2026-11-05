---
name: issues-to-outcomes
description: "Load before writing any report of work: a status update, an end-of-day or session summary, a handoff, a 'what landed' or 'what did you do' answer, or any reply built from a list of issues, PRs or commits. Also load when the reader says a report means nothing to them, asks what they experience, or asks for it at a high level. Turns issue and PR titles into outcomes the reader notices: how much of the work shows in the product, each visible change as before and now, and the invisible work as what was stuck or silently wrong and no longer is. Ships a checker the draft must pass before it is sent."
short_description: "Turn a list of issues into the outcomes the reader notices."
allow_implicit_invocation: true
metadata:
  when: "writing a progress report"
  situation: Reports and pages
---

# Issues to outcomes

A report of finished work answers one question for its reader: what is
different for me now? An issue number and its title answer a different one:
what did the tracker call it? Titles are written for whoever implements the
work. The reader of a report was not there and should not need the codebase in
their head to understand it.

## Who the reader is

Write for the person who uses the product and pays for the work. They notice
two things: what the product does when they use it, and what they or their
agents can or cannot get done while working on it. Everything in the report is
one of those two, or it is left out.

## The shape

Write the report in this order.

1. **How much of this can you see.** Open with one honest sentence on how much
   of the work shows up in the product. When the answer is "almost nothing",
   say exactly that and say what the work was instead. Do not open with a
   count of issues closed or PRs merged.

2. **What changed in the product, grouped by who notices.** One group for
   each kind of person who meets the change (the people who use the product,
   the staff who run it, the players, the admins), each under a bold label
   such as **What shoppers notice**. One item for each change that person can
   see, hear or do. A change that is real but shows nothing yet says so, and
   says what it makes possible later.

3. **What was stuck and is not any more.** The rest of the work, named by its
   consequence: what could not be done, or what was quietly wrong, and what is
   true now. When the reader is already seeing an effect of it, connect the
   two for them.

4. **What you will still run into.** Only when something the reader will hit
   is still broken or unfinished. Leave the section out when nothing is.

Group related work into one item. Five fixes to the same failure are one line
about that failure, not five lines.

## Writing each item

Each item is a bold headline, then the scenario that shows it:

> **Prices stay right after a refresh.** When a listing is refreshed overnight,
> its price no longer drops to the default markup; it keeps the markup its
> category sets.

- **The headline** names the change in the reader's words, short enough to scan
  down the list.
- **The scenario** is "When <the reader does or meets something>, <what used to
  go wrong> no longer happens; <what happens now>." For a new tool rather than
  a fix: "When you want <something>, you no longer have to <the old workaround>;
  <what the tool does>."

- Start from the reader's situation, never from the code. "A looped ability
  sound no longer gets stuck on forever when part of the effect fails to
  load", not "fix cue leak on partial load failure".
- Give the before and the now in that one scenario sentence. A fix the reader
  cannot picture before and after is not yet described.
- Use the words the reader uses for the product. Leave out type, function,
  file and rule names unless the reader has to open, run or search for them.
- Keep the proportions true. Plumbing is reported as plumbing. Do not dress a
  refactor as a feature, and do not pad a short list of visible changes.
- A reference goes at the end of its sentence, as a link, for the reader who
  wants the detail. It never opens a line and never stands in for the
  description.

## Example

A report that means nothing to its reader:

~~~md
- #1407 test harness raises only real engine events
- #1417 full verification works on the declared runner image
- #1422 and #1423, two cue leaks
- #1445 a cancelled ability tells its cues it was cancelled
- #1447 project code-style rules judge code again
~~~

The same work as what the reader notices:

~~~md
What you can see in the game from today's work: almost nothing. Nearly
everything that landed was plumbing.

**What players notice** (two small things):

- **Looped sounds stop.** When part of an ability's effect fails to load, its
  looped sound no longer plays forever with no way to stop it; it ends with
  the ability. The same holds when one of several targets fails
  ([#1422](https://example.com/1422), [#1423](https://example.com/1423)).
- **Cancelled abilities end as cancelled.** When you cancel an ability, its
  effects no longer end as if it finished normally; they end as cancelled.
  Nothing looks different yet; it lets effects fade differently on cancel
  later ([#1445](https://example.com/1445)).

**What was stuck and isn't** (you don't see it, but it blocked everything
else):

- **Verification runs again.** When an agent finishes a change, it no longer
  has no way to verify it on the current test machines; it can
  ([#1417](https://example.com/1417)).
- **Code-quality checks are back on.** When an agent writes code, the
  project's own checks no longer stay silently off; they judge it, which is
  why agents keep getting sent back with real findings tonight
  ([#1447](https://example.com/1447)).
~~~

## Before you send it

Run the draft through the checker that sits beside this file:

~~~sh
python3 <folder of this SKILL.md>/scripts/check_report.py <<'REPORT'
<the draft>
REPORT
~~~

It prints every line that opens with a tracker reference and exits non-zero
while any remain. Rewrite those lines and run it again; send the report once
it exits zero.

The checker cannot tell whether a line describes something the reader would
notice. That part is your judgment: read each item as someone who has never
seen the code and ask whether they could say what changed for them.
