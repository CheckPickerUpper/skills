Nothing breaks today for most migrations, and my "cleaner, more robust" was a label, not a reason. The concrete benefit is that a slow migration can no longer get your pods killed. That has happened once.

**What happens today**

Each of the 3 `acme/orders` pods runs `prisma migrate deploy` in its entrypoint before the server starts. Prisma takes a Postgres advisory lock, so the first pod applies the migration while the 2nd and 3rd wait on the lock. The server in none of them is listening during that time.

The probes in `deploy/orders.yaml` run during that wait (values as I read them earlier):

```yaml
# readiness
failureThreshold: 12
periodSeconds: 10
# ▸ Marked unready after 120s of failures.
# liveness
# ▸ Restarts the pod after 180s of failures.
```

**What went wrong on 2026-09-14** ([INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212))

1. Migration `20260914_add_orders_customer_idx` started on one pod and took 4m10s.
2. At 180s, the liveness probe started failing on all three pods, because none had a server listening yet.
3. All three pods were killed mid-migration.
4. They restarted and waited on the lock again.
5. The orders API was down for 19 minutes.

A pre-deploy Job moves the migration out of the pods, so the liveness probe never sees it. Your three pods stay out of the loop until the Job finishes, and `deploy.yml` can already run a one-off Job before rolling the Deployment.

**How often this matters**

Most migrations in the last 6 months took under 5 seconds. 2 of 41 took over 2 minutes, and both were index builds. INC-212 was one of the cases where a migration runs longer than the probe thresholds. Every migration is fine until one runs long, and then it takes the API down.

**What I couldn't confirm**

- I have not checked whether the new orders schema change includes an index build, so I can't say whether this deploy is exposed.
- I infer, but have not verified, that the old pods keep serving while the Job runs. That depends on the migration being compatible with the old code, which is true of an index build but not of every change.
- I haven't checked how the Job behaves if the migration fails or hangs, for example whether it has a timeout. That needs setting up either way.

**What decides it:** whether the migration can outlast the probe thresholds (180s for liveness). Below that, it works as it does now. Above that, as with INC-212, the pods get killed. A Job is the only option here where that limit doesn't apply. Raising the probe thresholds would also stop the kills, but it would slow how fast real failures are detected for the lifetime of the service.
