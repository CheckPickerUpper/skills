# concrete-why evals

Each file in `scenarios/` holds verified facts and a conversation that ends in a "why" or "why not"
pushback. A run answers every scenario twice with the same model: once from the scenario alone
(baseline) and once after reading `../SKILL.md`. A blind judge then scores each pair without being
told which reply used the skill. The A/B order alternates by scenario and is recorded in `key.txt`.

Judge criteria, 1–5 each: answers the side asked, concrete reasons, self-contained references,
honesty about the prior answer (including unsupported claims), decision usefulness, and economy.

## Runs

| Run | Skill version | Skill total | Baseline total | Notes |
| --- | --- | --- | --- | --- |
| 2026-10-07-v1 | first draft | 108 / 120 | 103 / 120 | Skill won s1 (27–26) and s3 (28–23), tied s2 (27–27, judge leaned baseline), lost s4 (26–27): it was too long and its deciding rule didn't fit every item. One sample per cell. |
