---
name: zen-of-checkpickerupper
description: "The Zen of CheckPickerUpper: twenty-one lines that judge designs, fixes, abstractions, types, structure, and questions, each expanded and traced to its source skill. Use when settling a design choice or an ambiguous question, choosing between options, judging whether a fix, abstraction, type, or layout is right, or when someone asks for the zen of checkpickerupper."
short_description: "Twenty-one lines for judging designs, fixes, abstractions, types, and questions."
allow_implicit_invocation: true
---

# The Zen of CheckPickerUpper

<what-to-do>
Judge a design, fix, abstraction, type, structure, or question against these
lines. Read the line, then its expansion. Open the source skill named in the
expansion only when that line decides the case and you need its procedure.
</what-to-do>

## The Zen

```text
Unrepresentable is better than validated.
A shape is better than a check, and a check is better than a comment.
The witness is not the writer.
Fix the class, not the case.
The earliest owner that knows is the right owner.
There should be one owner—and only one—for every fact.
Shape the type where it is built; never carve or loosen it downstream.
Absence is a state, not a hole.
The first instance is evidence, not the owner.
Strip the incident's words; what remains is the class.
The form decides, not the number of callers.
Although an invented knob is worse than none.
A second way to do a thing is a bug waiting to happen.
Prevalence is not proof.
Read the definition, not the name.
A bypass left open means the class is still open.
A timeout, retry, or catch does not make a bad state valid.
Structure exists to show ownership.
Every finding must survive its refutation.
A clean approval is a real answer.
If the rules can derive it, do not ask it.
```

## Each line, expanded

### 1. Unrepresentable is better than validated.

Make an invalid combination fail in the shape of the data: a sum type for
mutually exclusive states, a product type for data that exists together, a
closed public surface. A validator leaves the raw value forgeable and every
caller wondering whether validation ran. Runtime validation can enforce
behavior, but it does not close the class. Source: `correct-by-construction`.

### 2. A shape is better than a check, and a check is better than a comment.

This ranks enforcement. A type or schema that cannot spell the bad state beats
a runtime check that catches it, and a check beats a comment or doc warning,
which prevents nothing. Use the strongest form the language allows; when the
type system cannot express a property, say so instead of faking it with a
brand or cast. Source: `correct-by-construction`.

### 3. The witness is not the writer.

The crash site, the failing reader, the error message, and the consumer that
noticed are evidence. The fix belongs where the bad state is written. Find that
writer before changing anything; a fix at the witness is a patch. Source:
`fix-the-class`.

### 4. Fix the class, not the case.

A fix that stops this incident but lets a sibling case through has fixed
nothing general. Swap the incident's nouns for a sibling: if the same bad state
can still happen, the fix sits too low. Source: `fix-the-class`.

### 5. The earliest owner that knows is the right owner.

Climb toward the place that can make the bad state impossible to spell: the
judge, the source of truth, the schema or generator, the public surface, the
type, the constructor or parser, then the runtime writer. Accept a runtime
owner only after proving nothing earlier can carry the rule. Source:
`fix-the-class`.

### 6. There should be one owner—and only one—for every fact.

Two representations of one fact drift: a hand-written type beside a schema, two
enums joined by a mapping table, a status rebuilt from a label. Derive
everything from the one source and delete the conversion. An exhaustive mapping
between two spellings of one fact is evidence of the problem, not its cure.
Sources: `fix-the-class`, `type-driven-design`.

### 7. Shape the type where it is built; never carve or loosen it downstream.

Needing `Pick`, `Omit`, `Extract`, a cast, `Partial`, or a non-null assertion at
a use site means the upstream type has the wrong shape. Fix the type where the
value is created so every receiver gets exactly what it needs. Deriving from
one authoritative schema is fine; patching the shape at each use is not.
Source: `type-driven-design`.

### 8. Absence is a state, not a hole.

"Not there" is a real state. Model it as a named variant, such as present or
absent, and parse absence into that variant at the boundary. An optional, null,
or missing field that reaches a domain type is the defect, however it is
spelled. Source: `type-driven-design`.

### 9. The first instance is evidence, not the owner.

The feature where a need first appeared shows that a capability exists; it does
not get to name it, house it, or decide who may call it. When the first
feature's vocabulary or folder defines a general operation, that operation is
instance-bound. Source: `categorical-generalization`.

### 10. Strip the incident's words; what remains is the class.

Remove the names, files, screens, commands, and local lifecycle words the
example donated, then restate the bug or abstraction. If it still makes sense,
that sentence is the class. Add a word back only by showing every valid
instance needs it. Sources: `fix-the-class`, `categorical-generalization`.

### 11. The form decides, not the number of callers.

If the concrete code is a specialization of a combinator you can name in one
line with no invented parameters, extract it, even with one caller. "Only one
caller", "no second use yet", and YAGNI are not reasons to keep a general form
trapped in one place. Source: `categorical-generalization`.

### 12. Although an invented knob is worse than none.

The counterweight to line 11. A parameter, strategy seam, or config field with
no basis in what the operation requires is invented variation. Delete it and
state the smaller operation that remains. Sources:
`categorical-generalization`, `antimatter-code-quality-review`.

### 13. A second way to do a thing is a bug waiting to happen.

New code that repeats an existing capability under a different spelling makes
the codebase unpredictable, and the two paths drift. Compare by behavior, not
by name, then reuse, extend, generalize, or keep them separate with the
concrete difference named. Source: `antimatter-code-quality-review`.

### 14. Prevalence is not proof.

An existing pattern earns reuse by being correct and fitting the requirement.
"The codebase already does it this way" justifies nothing, and a defect
repeated ten times is still a defect, not a precedent. Source:
`antimatter-code-quality-review`.

### 15. Read the definition, not the name.

Open the definition at the line you cite: the fields, the variants, the body,
the callers. Names, docstrings, comments, and PR descriptions are claims about
the code. When the name and the definition disagree, the disagreement is a
finding. Source: `antimatter-code-quality-review`.

### 16. A bypass left open means the class is still open.

A correct owner does not close the class while another writer, fallback,
manual lane, or escape hatch can still create the bad state. Remove, redirect,
or seal every bypass before calling it fixed. Source: `fix-the-class`.

### 17. A timeout, retry, or catch does not make a bad state valid.

Stopping, retrying, catching, and falling back are control flow. They can be
real requirements, but they do not decide which states are valid. Used only to
hide a bad state, they are mitigation, not a fix. Sources:
`correct-by-construction`, `fix-the-class`.

### 18. Structure exists to show ownership.

Folders, nesting, and names should tell a reader who owns what and where the
next thing goes. Use the least structure that makes ownership, placement, and
growth clear. Depth, file count, and name length are prompts to look, never
verdicts. Source: `antimatter-codebase-structure-review`.

### 19. Every finding must survive its refutation.

Before reporting a problem, try to destroy it: it falls if it cannot be proven,
has no concrete before-and-after, or would change behavior. Findings inflated
to look rigorous bury the real ones. Sources: `antimatter-code-quality-review`,
`antimatter-codebase-structure-review`.

### 20. A clean approval is a real answer.

When nothing survives refutation, approve without qualification. A finding
manufactured to look thorough is a failure of the review. Sources:
`antimatter-code-quality-review`, `antimatter-codebase-structure-review`.

### 21. If the rules can derive it, do not ask it.

Before asking anyone, consult the governing standard, the project's rules, and
the code, and record which settled it. Offer only options that pass every rule.
Never ask for a fact whose only use is narrowing a general design to today's
callers. Source: `fix-the-class`.
