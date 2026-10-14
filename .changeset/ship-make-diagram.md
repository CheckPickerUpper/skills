---
"checkpickerupper-skills": minor
---

Ship **`make-diagram`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`make-diagram` (model-invoked) makes an agent draw any diagram (a system map, flowchart, pipeline or process map) that a stranger can read. It settles the domain with the owner before drawing and keeps the owner's wording corrections in a words file. The mechanism is drawn as more nodes rather than longer box text, every check is a diamond with labelled yes and no branches, and each source of truth gets its own lane. Arrows carry semantic colours with a legend, and the drawing carries no captions or notes.

- `scripts/check_diagram.py` renders each diagram in light and dark themes, writes both images for the agent to look at, and refuses text under 15px, overlapping or clipped labels, labels on lines, boxes over three short rows, floating nodes and text, decisions missing a labelled yes or no branch, backward or crossing arrows, arrow colours that break the legend, captions, low contrast, and phrases the owner corrected.
