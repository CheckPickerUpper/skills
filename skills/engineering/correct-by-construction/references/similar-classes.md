# Similar classes: where else the same shape can happen

Load this only after the original class is closed, with its stripped class
sentence, its rule, its owner, its before-it-runs barrier and its proof, or
when the user asks where else the same bug can happen. If any of those is
missing, or the original bad state can still be written, return to the
protocol first: this is not a way to climb one more level on the same bug.

## Protocol

1. **Freeze the original class.** Restate its stripped sentence and say what
   belongs to it and what would be a different, sibling class.
2. **Generate siblings from the shape, not the incident nouns.** Look for
   neighboring domains with the same structure: another proof split, another
   raw value where a domain value is required, another client and server
   mismatch, another generated and hand-written split, another config and
   runtime disagreement, another public surface accepting primitives where it
   should accept a constructed value.
3. **Test each candidate with the same question:** can source, config,
   generated output, a public API call or a raw data shape still spell the
   transposed bad state directly?
4. **Give each exactly one verdict:**
   - **Closed:** an existing type, schema, generator, constructor, parser,
     registry or public surface rejects the shape.
   - **Open sibling:** a sibling class can still spell it and needs its own
     run of the protocol.
   - **Leak in the original:** not a sibling but a bypass inside the original
     class. Stop the sweep and return to the protocol with it as evidence.
   - **Not applicable:** the candidate lacks the rule this class depends on.
5. **Act only on the asked scope.** A sweep reports; fixing runs the protocol
   once per open sibling, one class at a time.

## Report

In full sentences, after restating the original class, its rule, its owner
and its barrier: what belongs to the original class and what does not, then
each candidate with its verdict, the evidence (the file, surface or proof, or
why the rule does not apply), and the next step.

## Never

- Reuse the incident's nouns as the search plan.
- Count search hits as proof that a sibling is open.
- Treat a bypass in the original class as a similar class.
- Call a sibling closed because a runtime writer checks it while raw source or
  data can still spell the bad state.
- Merge several open siblings into one vague class without proving one shared
  owner closes all of them.
