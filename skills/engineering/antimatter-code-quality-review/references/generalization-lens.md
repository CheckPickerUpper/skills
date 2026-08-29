# Generalization lens

Two findings live here and they point opposite ways. Run both: a review that only looks for duplication approves every knob nobody turns, and one that only looks for over-abstraction approves every form written twice.

## Direction one — the form is written twice

Ask: **can you name the general form in one line, inventing no new parameters?**

If yes, the second hand-written copy is the finding, and the `after` is the named form with both sites pointing at it.

- `particleEmittersIn(root)` is `descendantsOfClass(instance, className)`.
- `sumContributions(list)` is `sumBy`.
- Two constructors that each switch a string to pick a kind are one constructor per kind.

**Consumer count decides nothing.** "Only one caller", "no second instance yet", "nothing outside this domain reads it" are not evidence, and none of them survives Phase 2 as a refutation. The form is the argument. You would never refuse to write `add(a, b)` because nothing calls it twice.

The one thing that does refute it: naming the form requires inventing a config knob, a strategy seam, or a type parameter to hold variation that has no shape yet. That is direction two, and the answer is to leave the code alone.

## Direction two — a parameter no instance supplies

Ask: **does any instance supply a different value for this?**

If every instance passes the same thing, the parameter is not variation, it is a constant with a longer name. The `after` is deletion.

The same question catches a type parameter with one argument, a strategy interface with one implementation, and a config field every caller sets identically.

## The vocabulary check

Before accepting any name in either direction, quarantine the words the first instance donated: proper nouns, file names, screens, commands, framework terms, repo habits, and local lifecycle words such as `install`, `wire`, `setup`, `mount`.

Restate the abstraction with those words gone. If it stops making sense, the first instance still owns it and the name is not general yet. Add one word back only after showing it defines every member of the class.

## Verdict

Report a survivor as one of these, so the reader knows which way the fix runs:

- **Form written twice** — name the combinator, point both sites at it, migrate the siblings in the same change.
- **Variation invented** — delete the axis, restate the smaller invariant, and name the concrete second use that would earn it back.
- **Named by its first instance** — give the replacement name and what the instance words were hiding.

A change that extracts a genuine form and gains its second consumer in the same diff is a clean approval on this dimension, and worth saying so: it is the move this lens exists to encourage.
