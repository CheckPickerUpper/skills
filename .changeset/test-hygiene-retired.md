---
"checkpickerupper-skills": major
---

Retire **`test-hygiene`** and ship **`ruthless-bottleneck-destroyer`** in the **Engineering** bucket in its place.

**`ruthless-bottleneck-destroyer`** (model-invoked) holds everything `test-hygiene` did and more: every test, hook, gate and CI job has something to catch, catches its break, is the only check that does, runs only when its inputs change, and costs only what its claim needs.

- Upgrade: anything that loads `test-hygiene` by name loads `ruthless-bottleneck-destroyer` instead.
