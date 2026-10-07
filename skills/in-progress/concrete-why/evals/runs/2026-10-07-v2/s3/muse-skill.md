**Short answer:** Move migrations to a pre-deploy Job. My earlier "cleaner, more robust pattern" was a label, not a reason — the reason is it stops a long migration from taking the API down again.

**Fast migrations — 39 of 41 in the last 6 months, under 5 seconds:** what they are is the normal schema change; today each of the 3 `acme/orders` pods runs `prisma migrate deploy` in its entrypoint, and the Postgres advisory lock makes pods 2 and 3 wait instead of applying twice.
- *If we keep entrypoint:* pods wait a few seconds on the lock, start well before the probes in `deploy/orders.yaml` — the file that marks a pod unready after 120s and restarts it after 180s of failures — fire. No user-visible difference.
- *If we move to a Job run by `.github/workflows/deploy.yml` — the pipeline that can run a one-off Job before rolling the Deployment:* one Job applies the migration once, new pods start. No user-visible difference either.

**Slow migrations — 2 index builds over 2 minutes, including `20260914_add_orders_customer_idx`:** what they are is the exception that decides this; they outlast the probes above.
- [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), 2026-09-14: that index migration took 4m10s. That is what happened when it ran in the entrypoint — all three pods passed 120s and went unready, then passed 180s and were killed by the liveness probe mid-migration, restarted, and re-waited on the lock. Orders API callers got no healthy pod for 19 minutes.
- *If we move to a pre-deploy Job:* the Job has no 180s pod liveness kill, so it runs the 4m10s to completion, and the Deployment rolls only after. Old pods keep serving until new pods start against the migrated schema.

**What decides it:** whether the migration outlasts the 180s liveness restart in `deploy/orders.yaml`. Under it, location doesn't matter; over it, entrypoint repeats INC-212.
