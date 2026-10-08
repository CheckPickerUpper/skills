Each `acme/orders` pod runs `prisma migrate deploy` before its server starts, so all three pods wait on one Postgres advisory lock during every deploy. Run that command once in a pre-deploy Job before the Deployment rolls, and pods start without waiting, so a migration that takes 4m10s no longer restarts them mid-run.

**How orders starts today**

`acme/orders` is the service running on Kubernetes with 3 replicas, whose pods each run migrations at boot before serving. Each pod's entrypoint runs `prisma migrate deploy`, the Prisma command that applies pending schema migrations, before starting the server; the server start waits on it. Prisma, the tool that runs that command, takes a Postgres advisory lock during `migrate deploy`, so the first pod applies migrations while the 2nd and 3rd pods wait on the lock instead of applying twice.

`deploy/orders.yaml` is the Kubernetes manifest that sets the Deployment's probes, checked on each pod. The readiness probe has `failureThreshold: 12, periodSeconds: 10`, so a pod is marked unready after 120s of failures. The liveness probe restarts a pod after 180s of failures. I infer probes fail while `migrate deploy` runs, from the migrate-before-server order, because the server isn't up to answer them yet.

```
// today, in each pod entrypoint
prisma migrate deploy
// ▸ Applies pending migrations; first pod holds the Postgres advisory lock, 2nd and 3rd wait.
// ...
```

**The 19-minute outage**

[INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) is the 2026-09-14 incident where the orders API was down 19 minutes during an index build. `20260914_add_orders_customer_idx`, the migration that added the customer index on orders, took 4m10s (250s).

1. Deploy starts 3 new pods. Each runs `prisma migrate deploy`. One acquires the advisory lock, two wait.
2. The index migration runs 250s, past the 120s readiness mark and the 180s restart mark.
3. After 120s, pods count as unready; after 180s, the liveness probe kills all three pods mid-migration.
4. Pods restart, re-run `migrate deploy`, re-wait on the lock, and are killed again while the migration still runs.
5. The orders API has no ready pods for 19 minutes.

This happens only when a migration outlasts the 180s restart timeout. It does not happen for the common case: most migrations in the last 6 months took under 5 seconds, far below 120s. It lines up with the rare case: 2 of 41 migrations in that window took over 2 minutes, both index builds.

**What a pre-deploy Job changes**

`.github/workflows/deploy.yml` is the deploy pipeline that rolls the Deployment, and it can run a one-off Kubernetes Job before rolling. In that shape the Job runs the migration once to completion, then the Deployment rolls pods that start without a migration wait.

```
// option: Job in .github/workflows/deploy.yml, before the Deployment rolls
prisma migrate deploy
// ▸ Runs once in the Job; the Deployment rolls after it finishes, so pods start without waiting on migration.
```

For migrations under 5 seconds, there is no observable difference: pods wait a few seconds either way and probes never reach 120s. For an index build over 180s, the difference is pods restarting in a loop with no ready pods versus the Job finishing once and new pods then starting at once. Because 2 of 41 recent migrations took over 2 minutes, a future index build can outlast 180s and leave the orders API with no ready pods again if it stays in the entrypoint.

My earlier "It's the cleaner, more robust pattern." was a label, not a reason. The reason is the loop above.

**What decides it:** whether the migration can outlast the pod's 180s liveness timeout — if it can, it can't run where that timeout can kill it.
