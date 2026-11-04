---
name: build-vs-buy
description: "Run on every new feature, capability, service, integration or mechanism before writing code, and again on the code once it exists. That includes code an agent writes for its own work: a scratch script, a test harness, a test runner, an audit or measurement tool. Use before adding or swapping a dependency; before writing streaming, pub/sub, push, retries, rate limits, tokens, parsing, decoding, validation, money, dates, fake time, test waits, mutation testing, per-test timing, background jobs, browser automation, CLI parsing, logging or any other standard capability; when someone asks 'is there a library', 'what should we use' or 'don't hand-roll this'; when a fix means aliasing, stubbing, shimming or excluding a dependency; and when reviewing code or a diff that may hand-roll what an existing dependency, the platform or a maintained library already owns. Reads the repository's declared library choices and manifests, names the standard approach, maps coverage, picks one owner (reuse, adopt, buy, build, combine or defer), records the decision where the work is tracked, and audits written code for hand-rolled standard parts."
metadata:
  when: "starting a new feature or mechanism, choosing a dependency, or reviewing code that may hand-roll a solved problem"
  situation: Planning and design
---

# /build-vs-buy

Every capability has an owner: code the project already has, a dependency it
already declared, the language or platform, a maintained library, a managed
service, or custom code. Choose the owner before writing the implementation,
and check the choice again once code exists. Custom code is for what no other
owner covers, and that is a recorded decision, never a default.

The result is one evidence-backed decision, not a catalog of options.

## Never

- Write a mechanism before this skill has chosen its owner.
- Treat code written for your own work (a scratch script, a test harness, a
  runner, an audit tool) as outside this skill. It is code, and what it does
  usually has a name and a standard tool: breaking code to prove tests fail is
  mutation testing; timing and limiting tests is the test runner's job.
- Treat a request for a library as a request for a package name, or let the
  first example name the solution.
- Hand-build a standard part because no single library owns the whole
  outcome; combine owners instead.
- Treat popularity, familiarity, precedent, sticker price or diff size as
  evidence of fit. They are search signals.
- Present a package as current, maintained or compatible from memory. Check a
  primary source, or mark the fact unverified.
- Install a dependency, buy a service, create an account or change production
  configuration without the user's authorization for that path.
- Leave the decision only in the conversation.
- Reject a candidate for a reason that holds only if the custom code stays
  beside it. Judge every candidate as the replacement.
- Rest a decision on an unverified fact. When one documentation tool is
  unavailable, read the official site. A claim that nothing offers a
  capability needs the search that shows it.
- Offer an option that misses a hard requirement as a trade-off for the user
  to accept. Report it as rejected, with the requirement it misses.

## Standard capabilities

Treat each of these as owned by something other than new custom code until the
search shows otherwise. A diff or plan that contains one triggers this skill.

| Area | Capabilities |
| --- | --- |
| Data in and out | parsing, decoding, serialization, schema validation, configuration loading |
| Network | HTTP clients and servers, retries and backoff, rate limiting, timeouts, connection pooling |
| Events | streaming, pub/sub, database notifications (such as LISTEN/NOTIFY), server-sent events, websockets, push notifications |
| Work | background jobs, queues, scheduling, leases, concurrency primitives |
| Identity | authentication, sessions, tokens (JWT, JOSE), password hashing, cryptography |
| Values | decimal money and currency, dates, times and time zones, locale formatting, units |
| Storage | database drivers, query builders, migrations, generating migrations from a declared schema, caching, file paths, temporary files, atomic replace |
| Interfaces | command-line parsing, routing, forms, state management, UI components, icons |
| Tests | mutation testing, per-test timing and time limits, fake time and clocks, waiting for events, fixtures and test databases, browser automation and pooling, snapshot and golden files, selecting tests and checks by changed files, per-step time limits |
| Operations | logging, tracing, metrics, error reporting, feature flags |
| Code | collection algorithms, text and diff utilities, code analysis and generation |

## Before the code

<what-to-do>
1. **Freeze the outcome.** State the user-visible result in one plain
   sentence, apart from any proposed implementation, library or first example.
   Restate the problem with the repository's own nouns stripped ("server-only
   code reaching the browser bundle", not "this package breaks the build").
   Classify each requirement as hard, important or optional; label reversible
   assumptions. Scale the legwork to the risk: a local helper needs a focused
   check; a vendor, a sensitive data path, recurring spend, a public API or a
   hard-to-reverse migration needs full evidence.

2. **Read what the repository already chose.** First its declared library
   choices: an "use X for Y" table or library rule in `AGENTS.md`,
   `CONTRIBUTING.md` or equivalent, and any ADRs. Then the nearest manifests
   and lockfiles (`go.mod`, `package.json`, `Cargo.toml`, `pyproject.toml`,
   `pubspec.yaml`), relevant configuration, shared helpers and generated
   surfaces, and how the dependencies are actually used. An owner the project
   already declared is the strongest candidate, because it has already accepted
   that integration. If no project is available, say the existing stack was not
   checked.

3. **Name the standard approach and compare it with this repository.** Name the
   library, platform feature or pattern most teams use for the stripped
   problem, by its real name. The reference for the stack lists the usual
   candidates: [Go](references/go.md),
   [TypeScript and React](references/typescript.md),
   [Flutter](references/flutter.md), [Python](references/python.md),
   [Rust](references/rust.md). Then say what this repository
   does instead, and whether that is a real constraint (a comment, an ADR, a
   dependency or a contract proves it) or a habit nobody decided. When they
   differ, say plainly that the current direction is the wrong shape and what
   replacing it costs. When a candidate fails only because of a shape this
   repository chose (tests importing built output instead of source, a custom
   path layout), that shape is a finding: judge it against the standard
   approach first. A shape nobody decided never disqualifies a candidate.

4. **Close the candidate set,** searching by capability, not by the first
   tool's name, in this order:

   1. existing internal capabilities and declared dependencies;
   2. the language, platform or framework;
   3. maintained packages or open-source components;
   4. managed services or vendors;
   5. custom code.

   Name the unit each requirement works at (per file, per request, per row)
   and search for owners that work at that unit. A tool whose smallest unit is
   coarser than the need is not a candidate for that need.

   Check current primary sources (official documentation, repository, release
   history, licence, pricing, security notes, compatibility) when the decision
   depends on facts that change. Mark a fact `unknown after checking` when the
   evidence is unavailable.

5. **Map coverage and burden.** One row per requirement:

   | Need | Owner | Covered by | Custom remainder | Burden or risk | Evidence |
   | --- | --- | --- | --- | --- | --- |

   Apply hard gates first: correctness and fit, security and privacy, licence
   and compliance. Then weigh reliability, performance, total cost of
   ownership, operational ownership, extensibility and reversibility. Count the
   whole burden of an adopted or bought option: integration, migration,
   monitoring, upgrades, failure handling and eventual removal. An unknown
   stays unknown; it is never scored as zero.

6. **Choose one owner:**

   - `REUSE`: existing internal code or a declared dependency covers it.
   - `ADOPT`: the platform, standard library or a maintained package should
     own it.
   - `BUY`: a managed service or vendor should own it and its operations.
   - `BUILD`: the remaining behavior is genuinely specific to this domain, or
     every other owner violates a hard constraint.
   - `HYBRID`: separate owners cleanly cover separate parts; only their
     coordination is custom.
   - `DEFER`: an unresolved hard constraint blocks a correct choice.

   Choose `HYBRID` only when every boundary has an owner and the coordination
   is understood, and `BUILD` only after the search shows why nothing else
   fits. Add a new dependency only when no declared one covers the need.

7. **Record the decision** where the work is tracked: the issue body, or the
   commit body when there is no issue. The commit that lands the work names
   the libraries it uses and gives the reason for any new dependency.
</what-to-do>

Ask one focused question and stop only when an unresolved hard constraint,
spend, a new vendor or replacing an owner the repository declared could change
the decision. A reversible technical choice is decided, not asked.

**The signal you are already on the wrong path:** a fix that aliases, stubs,
excludes, polyfills or shims one name around a dependency, bundler or
framework, and then reveals another of the same kind, is not one fix short of
done. The approach was wrong at the first one. Return to step 1.

## After the code

Run this on any implementation, diff or plan that contains a standard
capability, whether or not the decision above was made. It asks whether custom
code carries a solved capability that another owner should carry.

<what-to-do>
1. **Pin the surface:** the changed files and the comparison point, the named
   files, or the proposal sections. Every conclusion traces to one of them.

2. **Read the owners available to that code:** the declared library choices,
   manifests and lockfiles, shared helpers, generated surfaces, and the
   language and platform capabilities. Name each source checked, and say so
   when a manifest is absent.

3. **Partition the surface** into standard capabilities (the table above) and
   project-owned behavior: domain policy, orchestration, integration glue, and
   adapters an external contract requires. Each changed custom block is one
   entry: the need, the current code, the existing project owner, the platform
   owner, a candidate library, the custom remainder, and the evidence.

4. **Verify owners** in the order: declared dependency or shared helper, then
   platform or standard library, then a library whose documentation and
   repository cover the behavior. Check the API, semantics, edge cases,
   compatibility, licence and maintenance from primary sources when they affect
   the decision. A candidate absent from the manifest is a new-dependency
   option, not an existing owner. Existence is not fit: a similarly named
   package replaces nothing until its documented behavior matches the
   project's constraints.

5. **Apply the replacement test.** Report a replacement only when the code
   performs a named standard capability, the owner covers the same behavior
   under the target's constraints, adopting it removes caller-owned work,
   duplicated semantics or a concrete failure surface, the custom remainder is
   genuinely project-specific, and the evidence names the manifest, API or
   documentation that proves the fit.

6. **Classify each entry:** `REUSE` (an existing owner already covers it),
   `ADOPT` (a verified new dependency is the better owner), `KEEP CUSTOM` (the
   behavior is project-specific or the candidate fails a stated constraint), or
   `OPEN` (evidence is missing; name the smallest check that settles it).

7. **When replacing one tool with another,** prove the replacement keeps the
   meaning: it runs on the same inputs with the same rules. Check a linter,
   validator or parser with a probe input that breaks each rule on purpose,
   because some tools silently ignore a rule or option they do not know.
   Also prove the replacement is the one that runs: the gate, hook or CI step
   calls the new tool. A probe passing through a command nothing calls proves
   nothing.
</what-to-do>

## Answer

Lead with the decision in one sentence, then write it out in full sentences
and short paragraphs, with a blank line between them.

Every row and sentence changes the decision. Leave out what already works,
who the work was sent to, other agents and their issues, and broken or
rate-limited tools.

**Before the code:** the outcome; what the repository already uses and what the
standard approach is, and whether they differ; the decision and the chosen
owner; what each owner covers and what stays custom, and why that remainder is
necessary; the standard parts not to hand-build; the operational owner, cost
and exit path when a service or new dependency is involved; the rejected
options and why, only when they change the decision; the evidence, with direct
primary-source links and any unverified assumption; the unknowns; and the next
safe step.

**After the code:** one verdict (`REUSE`, `ADOPT`, `KEEP CUSTOM`, `MIXED` or
`OPEN`), the outcome, the surface and the sources checked, then one numbered
block per capability with its classification and `file:line`, saying what the
code does now, the preferred owner, why, the change, the evidence and the
custom remainder. End with the next action.

The record written to the issue or commit holds the decision, the chosen
owner, the custom remainder, the reason for any new dependency, and the
evidence links.

## Example

Before the code, a request to "send a reminder email if an order is unpaid
after 24 hours":

The decision is `REUSE`: the project's declared job queue owns delayed work,
and its mail client owns sending.

The repository's `AGENTS.md` names a database-backed job queue for background
work, and the manifest already declares it and a mail client. The standard
approach for "run this later, once, and survive a restart" is a durable job
queue with scheduled jobs and unique keys, which the declared queue provides.
The proposal in the issue was a polling loop with a sleep; nobody decided that
shape, so it is the wrong one.

The queue covers scheduling, retries with backoff and at-most-once delivery
per order through a unique job key. The mail client covers sending. The custom
remainder is the rule "unpaid after 24 hours, and not cancelled", which is
domain policy. Do not hand-build the timer, the retry loop or the
duplicate-send guard.

After the code, on a diff that added `retryWithBackoff` in
`src/billing/charge.ts:40`:

The verdict is `REUSE`. The project already depends on a retry library with
exponential backoff, jitter and a retry-on predicate, used in
`src/http/client.ts:12`; the new helper repeats it without jitter, so many
clients retry in lockstep. Replace it with the declared library and keep only
the predicate that says which charge failures are retryable, which is the
billing policy.
