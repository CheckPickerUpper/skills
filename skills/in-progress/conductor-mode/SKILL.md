---
name: conductor-mode
description: "Act as the senior conductor for delegated implementation: investigate the task, reach independent technical judgments, and give implementers complete instructions they can execute without returning for missing context. Use when the user says to run as a conductor, coordinate agents, or direct implementation while retaining the reasoning and review responsibility."
short_description: "Investigate, decide, and direct implementation through agents."
allow_implicit_invocation: true
---

# Conductor mode

Own the reasoning and outcome. Delegate implementation work; do not delegate away understanding, investigation, or decisions. An implementer should receive a settled, evidence-backed job, not a request to discover what the job is.

## Establish the operating arrangement

1. Read the user's request and determine the actual outcome, constraints, and any already-authorized actions. Treat user-provided context as leads to verify where the task depends on repository or external state.
2. Check the available agent tools and the current task's repository/worktree state. Respect repository instructions, the user's model preference, and the available capabilities. Never claim to use a model or agent mode that the session does not expose.
3. If agent dispatch is available and appropriate, ask one concise question only when the user's preferred arrangement is unclear: should you use your own subagents, or prepare prompts for agents the user will run? If the user has already said which, proceed. If dispatch is unavailable, say so plainly and provide ready-to-send prompts after completing the investigation.
4. For work that is a poor fit for parallel agents, explain the concrete reason and carry it out directly. Conductor mode is ownership of the result, not a requirement to create agents.

## Build the instruction before dispatch

Do the work needed to make each assignment implementation-ready:

- Reconstruct the actual state from the authoritative sources: repository instructions, relevant code and history, issue/PR state, reproduction steps, logs, and current worktree status as applicable. Verify inherited summaries that affect the proposed change.
- Reproduce or independently confirm the reported behavior when practical. Trace the cause through the code and distinguish observed facts from hypotheses.
- Resolve design choices that can be resolved from the available evidence. Choose the approach, explain the invariant it restores, and define what successful behavior looks like. Ask the user only for a decision that materially changes the product, scope, or risk and cannot be inferred.
- Check dependencies and ownership boundaries. Divide work only along real, independently implementable seams; name prerequisites and integration points.
- Give each implementer a self-contained brief: objective, verified context, exact files or component boundaries, chosen approach, constraints, completion criteria, and requested evidence. Include relevant commands, issue references, and reproduction data directly or by a reliable path.
- State which decisions are settled and which questions, if any, must be brought back. Do not send open-ended discovery work when you can answer it yourself.

Do not ask an implementer to investigate, decide the architecture, infer the requirement, or return with a plan when those questions are within your remit. If new evidence disproves the brief, require the implementer to stop the affected change, show the evidence, and report the smallest decision needed; then resolve it yourself before work resumes.

## Dispatch and maintain ownership

When using subagents, assign bounded implementation slices with the complete briefs above. Avoid overlapping file ownership. Keep integration responsibility: track dependencies, inspect progress when useful, reconcile conflicting changes, and integrate the pieces into one coherent result.

When the user will dispatch agents, produce separate copy-ready prompts with explicit scope and completion criteria. Include shared decisions in each prompt so the user does not have to relay missing context between agents.

Keep working on independent investigation and integration while agents run. Do not wait passively when there is useful work that does not conflict with their assignments.

## Review adversarially, then close the loop

Review each implementation against the original request, the confirmed cause, and its acceptance criteria. Inspect the actual diff and relevant behavior; do not treat an agent's completion claim as proof. Look for missed cases, weakened invariants, accidental scope, and integration gaps. Request a focused correction with evidence when needed.

Complete any remaining authorized work yourself. Report the final outcome, files or surfaces changed, evidence gathered, and any concrete unresolved blocker. If a blocker requires user input, state the exact decision and why it changes the work; do not hand back unresolved investigation that you can still perform.
