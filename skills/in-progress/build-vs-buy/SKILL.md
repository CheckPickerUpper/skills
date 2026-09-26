---
name: build-vs-buy
description: "Before implementing a new capability, service, subsystem, or integration, choose its owner—reuse, adopt, buy, build, combine, or defer—when the decision spans internal code, platform adoption, managed services, or custom boundaries. Use library-fit for package-only coverage questions."
---

# /build-vs-buy

Choose who should own a capability before writing its implementation.

Use this as a pre-implementation gate when the choice could be an existing
internal capability, a platform or package, a managed service, custom code, or
a combination. For a package-only coverage question, use the package-focused
`library-fit` workflow when it is available.

The result is one evidence-backed decision, not a catalog of options.

## Procedure

### 1. Freeze the outcome

State the user-visible outcome separately from the proposed implementation.
Capture the scope, hard constraints, risk level, and non-negotiable
requirements. Preserve constraints already stated in the conversation. Use
reversible assumptions for missing low-risk details and label them as
assumptions.

Scale the legwork to the decision's risk. A small local helper needs a focused
check. A third-party service, sensitive data path, recurring spend, public API,
or hard-to-reverse migration needs full evidence.

Completion criterion: the desired capability is clear, every requirement is
classified as hard, important, or optional, and every decision-changing unknown
is visible.

### 2. Close the candidate set

Search for owners in this order:

1. Existing internal capabilities and project dependencies.
2. Platform, framework, or standard-library capabilities.
3. Maintained packages or open-source components.
4. Managed services or vendors.
5. Custom implementation.

Search by capability, not only by the name of the first proposed tool. Inspect
actual repository usage, ownership, contracts, and behavior. When external
facts matter, check current primary sources such as official documentation,
pricing, license or terms, security material, compatibility notes, and release
history. Mark facts as `unknown after checking` when evidence is unavailable.

Completion criterion: every credible owner has been checked, or the reason it
is not applicable is recorded; no candidate is included only because it is
familiar or popular.

### 3. Compare coverage and burden

Map each requirement to each candidate:

| Requirement | Candidate owner | Covered by | Custom work | Risk or burden | Evidence |
| --- | --- | --- | --- | --- | --- |

Apply hard gates before weighing trade-offs. Examine correctness and fit,
security and privacy, licensing and compliance, reliability and performance,
total cost of ownership, operational ownership, extensibility, and
reversibility.

Make the full boundary visible. Include integration, migration, monitoring,
support, upgrades, failure handling, and eventual removal in the burden of an
adopted or purchased option. Unknowns remain unknown; they do not become a
zero-cost or zero-risk score.

Treat popularity, familiarity, precedent, sticker price, and diff size as
search signals. Base the decision on fit, constraints, evidence, ownership,
burden, and reversibility.

Completion criterion: every requirement is covered, rejected, or explicitly
unresolved; each surviving candidate has a named operational owner; and all
custom work and material assumptions are visible.

### 4. Choose one owner

Return exactly one decision:

- `REUSE` — an existing internal capability satisfies the requirements.
- `ADOPT` — a platform, standard library, package, or open-source component
  should own the standard capability.
- `BUY` — a managed service or vendor should own the capability and its
  operational burden.
- `BUILD` — the capability is genuinely domain-specific, or available choices
  violate a hard constraint.
- `HYBRID` — separate owners cleanly cover separate parts of the outcome.
- `DEFER` — an unresolved requirement or constraint blocks a correct choice.

Choose `HYBRID` only when each boundary has a clear owner and the coordination
surface is understood. Use `BUILD` only after the candidate search shows why
reuse, adoption, or purchase cannot satisfy the requirements.

Completion criterion: one owner is selected with evidence, rejected
alternatives, and a concrete reason the chosen boundary preserves correctness.

### 5. Record the decision boundary

Return this compact record:

```text
Mode: build-vs-buy
Outcome: {user-visible result}
Decision: REUSE | ADOPT | BUY | BUILD | HYBRID | DEFER
Chosen owner: {capability, tool, service, or custom boundary}
Coverage: {what the owner supplies}
Custom boundary: {what remains custom, if anything}
Operational owner: {who runs, upgrades, supports, and removes it}
Cost and reversibility: {material assumptions and exit path}
Rejected options: {alternatives and the reason for rejection}
Evidence: {repository paths and current primary sources}
Unknowns: {facts that remain unresolved}
Next safe step: {implementation or focused question}
```

Completion criterion: the record contains one decision, complete coverage,
explicit custom work, evidence for material claims, labeled unknowns, and a
next step that does not silently commit the user to a different option.

## Stop conditions

Ask one focused question and stop when an unresolved hard constraint could
change the decision. Return `DEFER` when the constraint cannot be resolved
within the available evidence.

The gate does not itself install dependencies, purchase services, create
accounts, sign agreements, or change production configuration. Perform those
actions only when the user's authorization covers the selected path.
