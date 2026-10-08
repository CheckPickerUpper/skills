Running migrations in the pod entrypoint causes the Kubernetes liveness probe to kill the pod if a migration takes longer than 3 minutes, taking the API offline. Moving the migration to a pre-deploy Job runs it to completion before the new pods start.

I earlier said a pre-deploy Job is the "cleaner, more robust pattern". Those were labels, not reasons. Here is the concrete consequence of the current setup.

**How migrations run on pod start today**

`acme/orders` is the service that runs the orders API. It runs on Kubernetes with 3 replicas. Today, each pod runs `prisma migrate deploy` in its entrypoint before starting the server. Prisma takes a Postgres advisory lock so concurrent pods do not apply the same migration twice; the 2nd and 3rd pods wait on the lock.

**What a long migration breaks**

In `deploy/orders.yaml` (the Kubernetes configuration for the orders service), probes dictate how long a pod can take to start before it is killed:

```yaml
// deploy/orders.yaml
        livenessProbe:
          // ...
          // ▸ Restarts the pod after 180s of failures.
        readinessProbe:
          failureThreshold: 12
          periodSeconds: 10
          // ▸ Marks the pod unready after 120s.
```

While 39 of the 41 migrations in the last 6 months took under 5 seconds, 2 were index builds that took over 2 minutes. When a migration exceeds 180 seconds, it triggers the exact failure seen in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212):

1. A deployment begins, launching 3 new pods.
2. Pod 1 acquires the Postgres lock and starts migration `20260914_add_orders_customer_idx`. Pods 2 and 3 wait on the lock.
3. At 180 seconds, the migration is still running. The liveness probe fails for all 3 pods.
4. Kubernetes kills all 3 pods mid-migration.
5. The pods restart, Pod 1 re-acquires the lock, and the 180-second cycle repeats.
6. The orders API is down for 19 minutes because the 4m10s migration can never finish.

**The benefit of a pre-deploy Job**

The deploy pipeline (`.github/workflows/deploy.yml`) is the GitHub Action that rolls out new code. It can run a one-off Kubernetes Job before rolling the Deployment.

1. The deploy pipeline starts the migration Job.
2. The Job runs the 4m10s migration to completion. It has no liveness probe.
3. The pipeline rolls the Deployment, starting the 3 new pods.
4. The pods start immediately without waiting on locks or running migrations.

**What decides it:** can the migration process be killed if it takes longer than 3 minutes? A pod liveness probe kills it; a deploy pipeline Job does not.
