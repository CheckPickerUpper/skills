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

## Relationships

- Correctness can justify a convention.
- Convention cannot justify correctness.
- A canonical lane must still name the bug it prevents.
