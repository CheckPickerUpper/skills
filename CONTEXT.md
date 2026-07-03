# CheckPickerUpper Skills

## Language

**Correctness**
The invariant-preserving reason a design should exist. Correctness names the bad state prevented, not the house style copied.

**Convention**
Evidence that something is already common in a codebase. Convention can coexist with correctness, but it is never proof of correctness.

**Prevalence**
How widespread a pattern is. Prevalence is not evidence; a wrong pattern can be common.

**Canonical lane**
The route a codebase currently treats as blessed. A canonical lane is still wrong if it preserves an invalid state or makes the real invariant optional.

**Severity theater**
Inventing or inflating findings to satisfy a "be harsh" instruction. The dominant failure mode of an aggressive review: it buries real signal in noise and the reader stops trusting the tool.

**Refutation gate**
An adversarial pass whose job is to kill a finding, not confirm it. A finding is reported only if it survives. The gate is what makes a review strict without becoming severity theater.

**Behavior-preservation**
Proof that a proposed restructuring changes structure without changing what the code does — a pure move, test coverage, or a type check. A refactor suggestion that cannot show it is a flagged risk, not a recommendation.

**Blast radius**
How much breaks if a symbol changes — call sites, modules, flows. It ranks findings: severity is a concrete consequence, not an adjective.

## Relationships

- Correctness can justify a convention.
- Convention cannot justify correctness.
- A canonical lane must still name the bug it prevents.
- A finding must survive the refutation gate before it is reported.
- A restructuring must prove behavior-preservation before it is recommended.
