Most of the time there's no benefit. 39 of the last 41 migrations took under 5 seconds, and for those the entrypoint approach is fine. The benefit shows up only on a slow migration, and [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) is what that looked like.

On 2026-09-14, `20260914_add_orders_customer_idx` took 4m10s. Here is what happened, given the probes in `deploy/orders.yaml`:

- The first pod held the Prisma lock and ran the migration. Pods 2 and 3 waited on the lock, so none of them started the server.
- Readiness failed for every pod after 120s (`failureThreshold: 12` × `periodSeconds: 10`).
- Liveness killed every pod at 180s, in the middle of the migration.
- The restarted pods waited on the lock again, and the orders API was down for 19 minutes.

The migration runs inside the pod's startup, so the pod's health probes govern it. A migration longer than 180s therefore gets the pod killed. With a pre-deploy Job, the migration runs before the Deployment rolls. The Job has its own timeout, and the running pods keep serving the old version in the meantime. A slow migration then makes the deploy take longer, but it can't take the API down.

Two of the 41 recent migrations took over 2 minutes, and both were index builds. At that rate, roughly one migration in 20 is a risk. I haven't checked whether this schema change builds an index, so I don't know whether it's one of them.

There is a cheaper alternative. You could raise the probe thresholds, or add a `startupProbe` with a long allowance, so a pod can sit in migration for several minutes. That is a small change to `deploy/orders.yaml`. The downside is that a pod stuck in startup for a real reason would also take longer to be restarted.

My recommendation is still the Job. It fixes the cause of INC-212 rather than stretching the limits, and `deploy.yml` already supports running a one-off Job. If you'd rather keep this change small, the `startupProbe` is a reasonable stopgap. I'd then do the Job the next time a migration comes close to the limit.
