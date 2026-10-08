Moving migrations into a pre-deploy Job stops a slow migration from taking the orders API down, which is what happened in INC-212. Today it works fine for short migrations, and 39 of the last 41 were short. My earlier reasons, "cleaner, more robust pattern", were labels rather than reasons. The concrete reason is the incident below.

**What happens on a deploy today**

Each of the 3 `acme/orders` pods runs `prisma migrate deploy` in its entrypoint, and only starts the server after that finishes. Prisma takes a Postgres advisory lock while it migrates. That lock is a database-level "only one at a time" flag. Because of it, one pod applies the migration and the other two wait on the lock. None of the three serves traffic while it is waiting.

Two probes in `deploy/orders.yaml` watch those pods:
- **Readiness probe:** after 120 seconds of failures (`failureThreshold: 12` × `periodSeconds: 10`), the pod is marked unready and gets no traffic.
- **Liveness probe:** after 180 seconds of failures, Kubernetes restarts the pod.

A pod that is busy migrating fails both probes, because the server they check hasn't started yet.

**What happened in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) (2026-09-14)**

1. Migration `20260914_add_orders_customer_idx`, an index build, needed 4m10s.
2. At the 180-second mark, the liveness probe killed all three pods while the migration was still running.
3. The pods restarted, ran `prisma migrate deploy` again and waited on the lock again.
4. The orders API was down for 19 minutes.

This only happens when a migration takes longer than the 180-second liveness limit. Most migrations in the last 6 months took under 5 seconds, and those never come near it. 2 of 41 took over 2 minutes, and both were index builds.

**What changes with a Job**

`.github/workflows/deploy.yml` can run a one-off Kubernetes Job before it rolls out the Deployment. The Job runs `prisma migrate deploy` once, in its own pod. The server pods then start only after the migration is done. As a result:
- The server's liveness probe no longer watches the migration. I infer this from the fact that the Job would be a separate pod without the server's probes. I haven't written that Job spec yet.
- The running pods keep serving while the migration runs, because nothing replaces them until the Job finishes.
- A 4-minute index build becomes a 4-minute deploy instead of an outage.

**What it costs**

- A new step in `deploy.yml` that runs the Job and stops the rollout if the Job fails. Without that check, new pods could start against a schema that wasn't migrated.
- Old code keeps running against the new schema while the Job runs. This isn't a new constraint: today, the first new pod migrates while the old pods still serve.

**What I couldn't confirm**

- I haven't checked whether the new orders schema change is an index build or anything else slow. If it's a quick column add, today's setup would deploy it fine.
- I don't know what happened to the half-built index when the pods were killed in INC-212. The incident facts I have don't say.

**What decides it:** can any migration ever take longer than the 180-second liveness limit? 2 of the last 41 did, and one of them caused a 19-minute outage. As long as that can happen, migrating inside the pod entrypoint can take the API down, and a pre-deploy Job can't.
