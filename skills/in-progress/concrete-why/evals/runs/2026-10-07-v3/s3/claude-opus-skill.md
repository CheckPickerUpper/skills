For most migrations you get nothing out of it. The case it covers is the slow one that already took orders down once. In the last 6 months, 39 of 41 migrations took under 5 seconds, and those run the same way in either setup. The other 2 were index builds that ran over 2 minutes. One of those caused a 19-minute outage, because the pods' health checks killed them in the middle of the migration. A separate migration step stops the health checks from touching the migration at all. I still recommend the move. But "cleaner, more robust pattern" in my last message wasn't a reason. This is the reason.

**How it works today**

`acme/orders` runs as 3 copies (pods) on Kubernetes. When a pod starts, its entrypoint runs `prisma migrate deploy` and only then starts the server. Prisma takes a Postgres advisory lock for the migration. That's a database-wide "one at a time" flag, so the first pod applies the migration and the other two wait.

Two checks in `deploy/orders.yaml` watch each pod while it starts:

- **Readiness:** `failureThreshold: 12, periodSeconds: 10`. After 120s of not answering, the pod gets no traffic.
- **Liveness:** after 180s of failures, Kubernetes kills the pod and restarts it.

A pod running a migration isn't serving yet, so both clocks run during the migration.

**What happened in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) (2026-09-14)**

1. The deploy shipped migration `20260914_add_orders_customer_idx`, an index build that needed 4m10s.
2. One pod took the lock and started building. The other two waited on the lock. None of the three was serving.
3. At the 180s mark the liveness check killed all three. The migration was cut off before it finished.
4. The pods restarted, ran `migrate deploy` again and waited on the lock again, so the cycle repeated.
5. The orders API was down for 19 minutes.

This only happens when a migration runs longer than the health-check limits, and for the 2 slow ones it did.

**With a separate migration step**

The deploy pipeline (`.github/workflows/deploy.yml`) can run a one-off Kubernetes Job before it updates the pods. The new sequence would be:

1. The Job runs `prisma migrate deploy`. It has no readiness or liveness check, so a 4-minute index build finishes.
2. Meanwhile the old pods keep serving orders. Nothing restarts them.
3. Only after the Job succeeds does the pipeline roll out the new pods. They start the server straight away, so the health checks see a normal startup.
4. If the Job fails, the pipeline stops and the old pods keep running.

**What it costs**

- Changes to `deploy.yml` to run the Job, wait for it and stop if it fails.
- Removing `migrate deploy` from the pod entrypoint.
- Old pods now run against the new schema while the Job works. During today's rollout they may already do that briefly, but now it's guaranteed. So a migration has to stay compatible with the code that's already running, for example by adding a column before the code that uses it ships.

**The cheaper alternative**

You could raise the liveness limit above 180s instead. That would have saved INC-212, but each slower index build needs the limit raised again. It also means a pod that is genuinely stuck goes undetected for longer.

**What I couldn't confirm**

- I haven't looked at the new orders schema change yet, so I don't know if it's an index build or a 2-second column add. If it's quick, it would deploy fine either way this time.
- I don't know if the INC-212 index was built with `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks writes to the table while it builds, and a separate Job doesn't change that.

**What decides it:** can a migration take longer than the 180-second liveness limit? If it can, it should run somewhere without health checks. Two of the last 41 did.
