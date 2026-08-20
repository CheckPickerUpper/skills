---
name: skill-router
description: "Choose the one skill that best matches the user's current intent from the generated catalog, honoring explicit skill names and the alignment-to-review workflow. Use when the right skill is unclear or the user asks what to use next."
short_description: "Choose the next skill from the catalog."
allow_implicit_invocation: true
openai:
  interface:
    default_prompt: "Use $skill-router to choose the right next skill for this request."
    brand_color: "#475569"
catalog:
  stage: "routing"
  order: 0
  aliases:
    - "which skill should I use"
    - "route this task"
    - "what should I use next"
  when: "The user's intent is clear enough to route but the correct skill is not named."
  where_it_fits: "Entry point for discovery; it selects an exact skill name and then gets out of the way."
  success_signals:
    - "An explicit skill name is honored before any inferred route."
    - "A generic word alone does not trigger a route, and unclear intent is surfaced instead of guessed."
---

# Route to one skill

<what-to-do>

1. Read `references/skill-catalog.md`, which is generated from the published `SKILL.md` files.
2. If the user explicitly names `$skill-name`, honor that exact name and do not substitute a similarly named skill.
3. Otherwise match the user's intent to one complete alias phrase from the catalog. A generic word such as “review” or “tickets” is not enough.
4. Return one primary skill name, why it fits, and the next stage it hands off to. Include a predecessor first when the request is not ready for the chosen stage.
5. If no alias is a clear match, ask one focused routing question or explain the first missing decision. Never invent a skill name or a display-name override.

</what-to-do>

<supporting-info>

The router is a directory, not a second workflow owner. The catalog and each skill's `SKILL.md` remain the sources of truth; this skill only selects the next one.

</supporting-info>
