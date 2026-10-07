**Short answer:** Calling it "cleaner, more robust" earlier gave you a label, not a reason. The real benefit is narrower. It works fine today as long as a migration finishes in under 3 minutes. When one takes longer, the orders API goes down, and that already happened once. I still recommend the separate Job, because it costs one extra step in the deploy pipeline.

**How it works today:** each of the 3 orders pods runs `prisma migrate deploy` before it starts the server. Prisma takes a Postgres lock during the migration, so only one pod applies it while the other two wait. That part works, and it isn't the problem.

**The problem is the probes in `deploy/orders.yaml`.** A pod that is still migrating isn't serving yet, so its health checks fail. After 180 seconds of failed checks, Kubernetes kills the pod and restarts it.

**[INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212)** shows what that does. On 2026-09-14, the migration `20260914_add_orders_customer_idx` took 4m10s. Kubernetes killed all three pods partway through. They restarted and queued on the lock again, and the orders API was down for 19 minutes.

- *If we keep migrations in the pod startup:* any migration over 3 minutes can repeat INC-212. Over the last 6 months, 2 of 41 migrations took over 2 minutes, and both were index builds. Most of the other 39 finished in under 5 seconds.
- *If we move them to a Job before the rollout:* the migration runs in a one-off Kubernetes Job. Nothing restarts it after 3 minutes, so a 4-minute index build just takes 4 minutes. The new pods start only after the Job succeeds, so they never get killed mid-migration. If the migration fails, the deploy stops before any new pod starts. `.github/workflows/deploy.yml` can already run a Job before rolling the Deployment, so this means adding that step and deleting the migrate line from the pod startup.
- *For the 39 fast migrations:* nobody would notice a difference either way.

**What decides it:** whether a migration can run longer than 3 minutes. The index builds already have, so the Job is worth it.

I haven't checked how long this new schema change will take. If it builds an index on a large table, it's the same kind of migration that caused INC-212, and I'd want the Job in place before it ships.
