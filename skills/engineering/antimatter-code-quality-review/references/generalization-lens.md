# Generalization lens

<supporting-info>
Categorical generalization means identifying the behavior that stays the same
when the concrete instance changes. The first feature reveals the capability;
it does not own its name, placement, or permitted callers. **Instance ownership**
is the failure where that feature's vocabulary or boundaries define the general
operation.

Predictability comes from giving equivalent requirements a coherent shared
implementation and making necessary differences explicit. A familiar pattern
is a candidate to inspect, not proof that it is correct.
</supporting-info>

<what-to-do>
## Procedure

Run this for a proposed reuse, extension, extraction, competing implementation,
or abstraction whose name or flexibility is under review.

1. **Name the instance.** Identify the changed implementation and any existing
   counterparts by definition and caller locations. State what each does.
2. **Separate local words.** List names inherited from the first instance:
   feature, screen, command, file, provider, framework, or lifecycle terms.
   Restate the operation without them.
3. **Name the shared behavior.** Write one sentence describing the operation
   and guarantee that survive a change of instance. Check that sentence against
   the implementations, including their errors and side effects. If the words
   hide different requirements, record the differences before proposing reuse.
4. **Identify real variation.** Name the inputs, data, policy, or adapters the
   operation actually requires. Ground each in inspected behavior or explicit
   requirements. Separate instance-specific policy from the shared operation.
   Every proposed parameter or extension point must correspond to one of these
   differences; adding hooks to make unrelated implementations fit is invented
   variation.
5. **Check three unlike instances.** Use the original and two instances from
   different features or surfaces. Prefer inspected examples. Label plausible
   examples as hypothetical; they test the proposed name and boundary, not
   repository coverage or demand for extra configuration. For each, state what
   stays the same and what varies. Narrow the proposal when the operation only
   makes sense for the original, and remove flexibility the comparison did not
   establish.
6. **Choose name and owner.** Name the capability from the shared behavior.
   Restore a local word only after explaining why every valid instance needs
   that distinction. Keep a framework-required lifecycle name in its local
   wrapper. Place the shared operation with the owner of its guarantee; retain
   feature policy with that feature. A generic `utils` folder is not an owner.
7. **Write the resulting shape.** State which callers reuse it, which existing
   capability changes, which duplicate implementations disappear, and which
   necessary variants remain. Check behavior preservation for each affected
   caller. Report migration risk when equivalence cannot be established.

**Complete when:** the analysis identifies the shared behavior, necessary
variation, name, owner, three-instance check, and affected callers. It must
support a concrete before-and-after or reject the proposed abstraction with
the requirement it would violate.

## Decision rules

- **Reuse:** the existing capability is correct and already satisfies the new
  requirement. Point the changed caller at it.
- **Extend:** the same guarantee holds and a real requirement adds variation.
  Extend the owned capability while preserving its existing callers.
- **Generalize:** a nameable shared operation is confined to one instance or
  hand-written at several sites. Extract that operation and move instance
  policy to its callers. Account for relevant sibling implementations in the
  proposed migration.
- **Separate:** the guarantees, lifecycle, or ownership boundaries differ in a
  way that makes a shared implementation incorrect. Cite the concrete
  difference; superficial resemblance does not require unification.
- **Correct the pattern:** an existing implementation violates the required
  guarantee. Propose a corrected shared shape and account for affected callers.
  Repetition does not make the defect a valid precedent.

Consumer count does not decide generality. A single implementation can already
express a reusable operation. Judge parameters by the operation's requirements,
not merely by how many current callers pass different values. Remove a
parameter when it represents a constant fixed by the guarantee; retain an
input when the operation legitimately accepts different values.

## Verdict and finding evidence

Record one generalization verdict alongside the implementation decision:

- **INSTANCE-BOUND:** the first instance's name, policy, or placement still
  owns a shared operation. Give the replacement name, owner, and real variation.
- **GENERALIZED:** the name and owner express the shared operation, with
  instance differences supplied as inputs, policy, or adapters.
- **OVER-GENERALIZED:** the proposal invents variation or combines incompatible
  guarantees. Remove the invented flexibility or keep the operations separate,
  and state the smaller behavior each owns.

Carry the following into a surviving finding:

- changed and existing definition/caller locations;
- the shared guarantee and necessary differences;
- words inherited from the first instance;
- three-instance check, distinguishing observed from hypothetical examples;
- verdict and decision: reuse, extend, generalize, separate, or correct;
- concrete before-and-after, affected callers, and behavior-preservation basis.

Run the main skill's refutation gate before reporting a finding. A completed
analysis may support a clean approval. A different implementation is a finding
only when evidence establishes an unnecessary competing path and a concrete
correctness or maintenance defect.
</what-to-do>

<supporting-info>
## Examples

- A new export manually walks a tree for one object class while an existing
  selector performs the same traversal. Compare traversal order and scope;
  reuse or extend the selector when its guarantee fits. Calling the new code
  an export does not make tree selection export-owned.
- An HTTP endpoint and a background import independently enforce the same
  domain validation. Share the domain rule; retain request decoding and import
  error presentation at their respective boundaries. Their code can differ
  while the validation guarantee is the same.
- Two retry loops look alike, but one retries an idempotent read and the other
  can repeat a payment. Establish the operation's guarantee before combining
  them; visual similarity alone does not make the policies interchangeable.
</supporting-info>
