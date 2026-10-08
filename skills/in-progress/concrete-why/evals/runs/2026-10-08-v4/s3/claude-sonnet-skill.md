**Short answer:** Migrations that take under about 3 minutes work fine in the entrypoint, and most of yours take under 5 seconds. The Job helps only for a long migration, like the one in INC-212. That one took the orders API down for 19 minutes. My "cleaner, more robust pattern" wasn't a reason, just a label. The incident is the actual reason, and the sequence below shows how it happened.

**What happens today**

Each of the 3 `acme/orders` pods runs `prisma migrate deploy` in its entrypoint, and only then starts the server. Prisma takes a Postgres advisory lock (a database-wide "one at a time" lock), so one pod migrates while the other two wait on the lock. Nobody applies a migration twice. The server isn't listening until the migration finishes, so the probes in `deploy/orders.yaml` fail from the first second:

- Readiness (`failureThreshold: 12`, `periodSeconds: 10`) marks the pod unready after 120s.
- Liveness restarts the pod after 180s of failures.

**How that took orders down in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) (2026-09-14)**

1. The deploy started pods running migration `20260914_add_orders_customer_idx`, an index build.
2. One pod took the lock and began building the index. The other two waited on the lock.
3. No server was listening on any of the three, so every probe failed.
4. At 180s the liveness probe killed all three pods, while the migration was still running. It needed 4m10s (250s).
5. The pods restarted and waited on the lock again.
6. The orders API was down for 19 minutes.

This only happens when a migration runs longer than the 180s liveness window. Of your last 41 migrations, 2 took over 2 minutes, both index builds. Most of the rest took under 5 seconds, so "works fine now" is true for most deploys.

**What the Job changes**

`.github/workflows/deploy.yml` can run a one-off Kubernetes Job before it rolls the Deployment. The migration then runs in a pod that isn't covered by the Deployment's liveness probe, so a 4-minute index build can't get killed at 180s. Nothing rolls until the Job succeeds, so a failed migration stops the deploy instead of leaving restarting pods.

**What the Job costs**

- The pipeline gains a step.
- Old pods keep serving while the Job runs, so for a short time they run against the already-migrated schema. A schema change that breaks the old code, such as dropping or renaming a column, would need to be split into two deploys.

**Alternative:** Raising the liveness window above your longest migration also avoids a repeat. It makes the probe slower to restart pods that are actually broken, and it still depends on you guessing the longest migration.

**What I couldn't confirm**

- Whether the migration for this new orders schema change is an index build or another slow one. If it's a quick column add, the entrypoint will handle it as before.
- What the migration did when its pod was killed at 180s, and why the outage lasted 19 minutes rather than about 4. I only know the pods restarted and waited on the lock again.

**What decides it:** Can the migration run longer than the 180s liveness window? If yes, use the Job. If no, the entrypoint works as it does today, and you only need the Job for the next index build.
