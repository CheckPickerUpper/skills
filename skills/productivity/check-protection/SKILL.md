---
name: check-protection
description: "Choose verification before a full run, a repeated check, a review of existing evidence, or a check-cost audit. Ask what each check protects that existing or cheaper evidence does not; keep required gates and remove duplication."
short_description: "Choose checks by the protection they add."
allow_implicit_invocation: true
metadata:
  when: "deciding which checks are worth running"
  situation: Reviewing a change
---

# Check protection

<what-to-do>
Before spending time on a check, ask: **What does this protect that nothing cheaper already protects?** Name the plausible wrong behaviour it catches, the public boundary exercised, and the condition that would make the check fail. Read what the command actually runs, including nested scripts and profiles. A check's name, duration, or presence in an old brief does not answer the question.

Compare the proposed check with existing evidence: tested commit, input, environment, dependency versions, boundary and result completeness. Reuse a complete result when those conditions still cover the claim and the repository accepts that evidence. Inspect the recorded output rather than repeating the run to verify its author. A changed environment, conflicting evidence, incomplete verdict, or changed code on the exercised path can justify another run; state which condition changed.

Use the smallest supported check that catches the wrong behaviour at its real boundary. A deliberate-break proof needs the affected test, not the full repository. One plausible break per regression test proves that it can fail. A mock fallback does not add real-service coverage, and two profiles with the same test selection add no coverage. Client-wiring claims require the actual client; a native CLI proof covers only the native CLI boundary.

Keep gates required by the current repository and owner. Record a redundant required gate and propose changing its owner; run it until that requirement changes. Keep checks configured as they are: enabling a disabled gate, weakening a rule, or substituting tree identity for a required head-SHA run needs the owner's decision. After a rebase, use the repository's stated rules for static checks and affected modules. Reserve release-only, cold-cache and reproducibility checks for the changes or releases they protect.

Finish focused iteration and reviews before the final expensive proof when the repository permits that order. Compare re-reviews with the last reviewed commit. After an API-migration failure, find every known stale call pattern before starting another full run.

For an audit, inventory **every** check, including nested steps. Record one row per proposed command in a tab-separated file with this exact header:

```text
command	protection	cheaper	decision	reason	evidence
```

Use `run`, `narrow`, `reuse`, `omit`, or `wait` for `decision`. Name the cheaper check or write `none` with a reason. For `reuse`, link the existing complete result and its tested revision; for `wait`, name the dependency, its owner, and the external change that releases it. Put the record in the issue body or the task's durable decision log; keep operational logs and sensitive details out of public records.

Run `python3 <skill-folder>/scripts/check_decisions.py <record.tsv>` before acting on an audited plan and whenever its command list or decisions change. It rejects missing fields, invalid decisions and duplicate commands; it does not judge whether the claimed protection is true. Review each row for that judgment. A normal cheap iteration needs the question, not a separate audit file.

Measure a new expensive step on its first real run. Retry only when the failure can change without changing the command: a transient network failure can; an argument error or an hours-long quota refusal cannot. Check known capacity against the planned workload before launching a batch. Use the existing admission and routing controls; if waiting is necessary, name the actual unavailable resource or dependency rather than inventing a second queue.

Finish when every audited command has a decision, every retained check adds named protection or satisfies a current requirement, and every omitted or reused check has sufficient recorded coverage. Report what remains unproven. Changing the check policy is separate work with its own authorization.
</what-to-do>

<supporting-info>
The source examples are the [waste log](https://github.com/CheckPickerUpper/dotfiles/issues/1400). It records repeated full suites on an unchanged head, broad mutation runs, duplicate profiles, mock fallbacks mistaken for real-service proofs, and waiting without a dependency. Those examples motivate the question; their historical fixes are not universal commands or current policy.
</supporting-info>
