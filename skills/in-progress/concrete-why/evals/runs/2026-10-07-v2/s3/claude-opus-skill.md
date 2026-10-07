**Short answer:** It works fine as long as a migration finishes in under 2 minutes. When one runs longer, the current setup takes the orders API down, and that already happened once. Calling the Job "cleaner, more robust" wasn't a reason, but I still recommend it.

**What happens today with a slow migration.** Each of the 3 pods runs `prisma migrate deploy` before it starts the server. Prisma lets one pod hold a Postgres lock while it migrates, and the other two wait on that lock. While any pod is migrating or waiting, it fails its health checks. After 120s Kubernetes marks it unready and stops sending it traffic. After 180s it kills and restarts the pod.

**What that cost us before.** [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) on 2026-09-14 happened exactly this way. The migration `20260914_add_orders_customer_idx` needed 4m10s. Kubernetes killed all three pods in the middle of it. They restarted, waited on the lock again, and the orders API was down for 19 minutes.

**How often this comes up.** Of the last 41 migrations, 39 took under 5 seconds. Moving those to a Job changes nothing you'd notice. The other 2 took over 2 minutes, and both were index builds. Any migration in that slow group is where the current setup fails.

**If we move migrations to a pre-deploy Job** (`.github/workflows/deploy.yml` can already run one before it updates the pods):
- The migration runs once, in a pod that serves no traffic and has no health checks. A 4-minute index build just takes 4 minutes.
- Nothing kills it halfway and nothing waits on the lock, so the INC-212 restart loop can't happen.
- I infer that a failed migration would stop the pipeline before the pods are replaced, so the current pods keep serving. That follows from the Job running first; I haven't tested it.

**If we leave it as is:**
- Every migration under 2 minutes keeps working like today.
- Any migration over 2 minutes repeats INC-212.
- I haven't checked how long the new orders schema change will take. If it builds an index on a large table, it's likely to be in the slow group.

**What it costs:** one Job step added to the deploy workflow, and removing `prisma migrate deploy` from the pod startup command.

**What decides it:** whether any future migration can take more than 2 minutes. Index builds already have, twice in 6 months.
