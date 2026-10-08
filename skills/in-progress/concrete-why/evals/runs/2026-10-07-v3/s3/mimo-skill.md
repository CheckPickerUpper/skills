It works fine for 39 of the 41 migrations in the last 6 months. The benefit shows up on the other 2: today the pod running a slow migration is also the pod the liveness probe kills, and that turned a 4m10s index build into 19 minutes of orders API downtime in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) (2026-09-14). A pre-deploy Job takes the migration off the probe's clock.

My earlier line — "cleaner, more robust" — was not a reason. Here is what actually differs.

**How a deploy runs today**

`acme/orders` is the orders API, 3 replicas on Kubernetes. Each pod, in its entrypoint, runs the migration command before starting the server:

```sh
prisma migrate deploy   # ▸ Applies any migration not yet in the DB.
# ▸ Postgres advisory lock: pods 2 and 3 block here until pod 1 finishes.
./server                # ▸ Only reached after the migration completes.
```

`deploy/orders.yaml` — the Kubernetes manifest for this service — tells the cluster when a pod is broken while that is happening:

```yaml
readinessProbe:
  failureThreshold: 12
  periodSeconds: 10
  # ▸ 12 × 10s = 120s of failures and the pod is marked unready.
livenessProbe: {}
  # ▸ 180s of failures and Kubernetes kills the pod and starts a new one.
```

Nobody outside the cluster depends on these probes directly; they decide whether customers' orders requests reach a pod.

**What went wrong in INC-212, as it happens today**

Migration `20260914_add_orders_customer_idx` (an index build on the orders table, the kind that took over 2 minutes — 2 of 41 in the last 6 months) took 4m10s = 250s:

1. Each of the 3 pods starts its entrypoint and calls `prisma migrate deploy`. Pod 1 gets the advisory lock; pods 2 and 3 wait on it.
2. 120s in, no pod has opened its server port. The readiness probe marks all three unready — orders requests stop being routed.
3. 180s in, the liveness probe kills pod 1 mid-migration. The advisory lock is released with the connection; the half-applied migration is whatever Postgres rolled back to.
4. The restart makes a new pod 1, which calls `prisma migrate deploy` again, re-acquires the lock, and starts the index build again — from the start. Pods 2 and 3 are still waiting on the lock and are also killed at their own 180s marks.
5. The loop only ends when one pod's migration attempt finishes inside a 180s window that its probes haven't already expired. Orders API was down 19 minutes.

The same 250s migration run once by a pre-deploy Job looks like this: `.github/workflows/deploy.yml` (the deploy pipeline, which today can run a one-off Kubernetes Job before rolling the Deployment) creates the Job. The Job has no liveness probe, so nothing kills it at 180s. It holds the advisory lock for 4m10s, finishes, exits. Only then does the pipeline roll the Deployment, and the 3 new pods find the index already built; their `prisma migrate deploy` sees nothing to do and starts serving in seconds. During those 4m10s the **old** pods keep serving, so orders stay up — the deploy is slower by the migration's duration, and that is the whole cost.

**What changes for the 39 fast migrations**

Under 5 seconds is far inside both probe windows, so today's entrypoint runs them with no observable difference: pods start within the 120s readiness grace and nobody notices. Moving them to a Job changes nothing a user or on-call sees. The cost is the same one Job either way: one extra pipeline step that fails the deploy if the migration fails — which is the same failure the entrypoint has today, except it stops the rollout instead of crash-looping pods.

So the benefit is narrow and real: it does not touch the 39 migrations that "work fine now"; it removes the specific path where a migration slower than 180s gets killed and retried. That path cost 19 minutes of downtime once in 6 months, on index builds — which is exactly the shape of migration the new orders schema change may include.

**What I couldn't confirm:** the entrypoint file's path and exact contents (only that it runs `prisma migrate deploy` before the server); whether `deploy.yml` currently has the pre-deploy Job step wired or only the capability for one; and whether INC-212's 19 minutes contains any delay beyond the restart/re-wait loop.

**What decides it:** is the process applying the migration the same process a liveness probe will kill after 180s? If a migration can run longer than that, the thing running it must not answer to that probe — a Job doesn't.
