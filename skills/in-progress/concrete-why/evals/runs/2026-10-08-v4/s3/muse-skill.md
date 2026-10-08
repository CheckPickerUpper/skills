Each orders pod runs its migration step before its server starts, so the second and third pods to start wait while the first finishes. Moving that step into a Job that finishes before the new pods start keeps the migration wait out of the pods' startup probes.

**How orders deploys today**

`acme/orders`, the service that serves the orders API from 3 Kubernetes replicas, starts each pod by running `prisma migrate deploy`, the Prisma command that applies pending database migrations, in its entrypoint, the script that runs before the server starts. Prisma takes a Postgres advisory lock during that command, so the first pod to start applies the migration while the 2nd and 3rd pods wait on the lock with their servers not yet started.

The timeouts live in `deploy/orders.yaml`, the Kubernetes manifest that defines the orders Deployment, the controller that rolls the 3 server pods, and its health probes and that the kubelet on each node reads to decide whether to keep a pod: the readiness probe uses `failureThreshold: 12` with `periodSeconds: 10`, so a pod whose server never starts is marked unready after 120s, and the liveness probe restarts a pod after 180s of failures.

**What happened during the September index migration**

[INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), the 2026-09-14 incident in which the orders API was down 19 minutes, started from `20260914_add_orders_customer_idx`, the database migration that built an index for orders customers and took 4m10s to apply:

1. The Deployment rolls; all three new pods start their entrypoints and run `prisma migrate deploy`.
2. One pod takes the Postgres advisory lock and starts applying `20260914_add_orders_customer_idx`; the other two block on the lock with their servers not started.
3. After 120s the still-starting pods are marked unready; after 180s the liveness probe kills all three pods mid-migration.
4. The killed pods restart, re-run `prisma migrate deploy`, and block on the lock again.
5. The orders API was down 19 minutes.

This happens only when a migration runs longer than the 180s liveness window. Most migrations in the last 6 months took under 5 seconds and finish inside the probe windows; 2 of 41 took over 2 minutes, both index builds.

**What a pre-deploy Job changes**

`.github/workflows/deploy.yml`, the deploy pipeline that ships `acme/orders` and that can run a one-off Kubernetes Job, a pod that runs once to completion, before rolling the Deployment, can run `prisma migrate deploy` there instead. The Job applies pending migrations to completion, then the Deployment rolls; the new pods start, find no pending migrations, and start their servers without waiting on the advisory lock.

For a future index build that needs several minutes, that ordering can keep the new pods from being marked unready and restarted at 120s/180s, based on the 4m10s build in INC-212. The observable difference is in the new pods during the deploy: today they wait on the lock with servers stopped; with the Job they start at once. Against that, the pipeline does one extra migration run in the Job before each deploy.

My earlier "It's the cleaner, more robust pattern." was a label, not a reason. The reason is the sequence above: the entrypoint puts a 4-minute migration inside a 180s startup window.

**What decides it:** whether the migration must finish while new pods are already counting toward their 180s liveness restart.
