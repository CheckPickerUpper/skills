My earlier answer — "the cleaner, more robust pattern" — was not a reason. Both of those words are labels; I gave you no consequence. Here is what keeping migrations in the pod entrypoint actually costs: a migration that runs longer than your liveness probe gets the pods killed while it is still running. That is not hypothetical; it is [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), the 2026-09-14 incident in this service.

**What runs today, in order**

`acme/orders` runs on Kubernetes with 3 replicas, and each pod's entrypoint runs `prisma migrate deploy` before starting the server. Prisma takes a Postgres advisory lock for the migration, so exactly one pod applies a given migration and the other two sit waiting on that lock. Meanwhile `deploy/orders.yaml` gives the readiness probe `failureThreshold: 12, periodSeconds: 10` — a pod that is not ready after 120 seconds is marked unready — and the liveness probe restarts a pod after 180 seconds of failures. A pod running a long migration is not serving, so both probes are counting against it the whole time.

**How INC-212 unfolded**

1. The deploy rolled the pods. Each pod's entrypoint started `prisma migrate deploy` for `20260914_add_orders_customer_idx`, an index build on the orders table.
2. Pod A took the Postgres advisory lock and began building the index. Pods B and C blocked waiting on the same lock.
3. The index build ran 4m10s. Pod A served no traffic during this, so its probes failed.
4. At 180 seconds of failures, the liveness probe killed pod A mid-migration. Pods B and C were killed the same way, since the lock meant neither had finished its own `migrate deploy` either.
5. All three pods restarted, re-ran the entrypoint, and re-waited on the advisory lock for the still-incomplete index build.
6. That cycle repeated until the index finally completed, and the orders API was down for 19 minutes.

This is why "it works fine now" is true right up until it isn't. Of the 41 migrations in the last 6 months, 39 finished in under 5 seconds — those finish long before any probe notices the pod is busy, so boot-time migration looks free. The 2 that took over 2 minutes were both index builds, and both are in exactly the shape that hit you.

**What the pre-deploy Job changes**

`.github/workflows/deploy.yml`, the deploy pipeline, can run a one-off Kubernetes Job before rolling the Deployment. Moving `prisma migrate deploy` into that Job changes one thing: the migration no longer runs inside a pod that has probes pointed at it. A migration that takes 4 minutes now delays the rollout by 4 minutes, with the old pods still serving, instead of being restarted at 180 seconds and restarted again. The same 39 fast migrations cost a few extra seconds in pipeline time.

**What I couldn't confirm**

- I have not read `.github/workflows/deploy.yml`'s Job spec or the pipeline's timeout, so I cannot confirm what happens when the Job itself runs long — whether the pipeline fails the deploy cleanly or hangs. That needs checking before this lands.
- I have not confirmed the Job's `backoffLimit` and whether a failed migration blocks the rollout. The whole benefit depends on a failed Job stopping the Deployment update; if it doesn't, you have moved the failure without containing it.

**What decides it:** does the migration run inside a pod whose liveness probe enforces a fixed 180-second deadline? Migrations take as long as the table takes, not as long as the deploy allows; anything running under a liveness probe must beat that deadline every time, and an index build on a large table cannot promise that.
