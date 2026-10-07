It works fine until a migration runs longer than the probes allow, and that has already caused an outage.

[INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) (2026-09-14) is the case. The migration `20260914_add_orders_customer_idx` took 4m10s. The liveness probe restarts a pod after 180s of failures, so all three pods were killed mid-migration. They restarted and waited on the lock again, and the orders API was down for 19 minutes.

Two things in the current setup make that happen:
- **Every pod runs the migration.** One pod holds the Prisma advisory lock and the other two wait on it. If the migration outlasts the probe window, all three are killed together.
- **The pods that wait can't serve traffic.** Boot is blocked until the migration finishes, so a slow migration means no healthy pods.

With a pre-deploy Job, the migration runs once, outside the pod probes, so a 4-minute index build can just finish. The old pods keep serving traffic while it runs, and the Deployment only rolls after the Job succeeds. A failed migration also stops the deploy instead of putting pods into a restart loop.

How often this bites: 2 of the last 41 migrations took over 2 minutes, and both were index builds. The other 39 took under 5 seconds, so most deploys would see no difference.

If the new schema change is a quick column add, the current setup will probably be fine this time, and the Job is insurance against the next slow one. I haven't checked how long this migration will take. If it adds an index on a large table, I'd move it to the Job now.

The Job adds a pipeline step and one more thing to debug when a deploy fails. The cheaper alternative is to add a startup probe, or raise the liveness threshold well above your longest migration. That fixes the kill-loop but still blocks all three pods during a slow migration.

I'd go with the Job. Do you want it, or the probe change?
