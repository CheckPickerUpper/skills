It mostly works, but it broke once. On 2026-09-14, in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), the orders API was down for 19 minutes. Moving migrations into a separate Job fixes the cause of that outage.

**What went wrong:** each pod runs the migration before it starts the server, so the pod's health checks count the migration time against it. The liveness probe restarts a pod after 180s. The `20260914_add_orders_customer_idx` index build took 4m10s, so all three pods were killed partway through. They restarted, waited on the migration lock again, and were killed again. No pod got past the migration, so nothing served orders.

**What the Job changes:**
- **The migration runs once, with no probe to kill it.** The pipeline runs it as a one-off Job before rolling the Deployment. A 4-minute index build simply takes 4 minutes.
- **The old pods keep serving while it runs.** The rollout only starts after the migration succeeds, so a slow migration means a slow deploy, not an outage.
- **A failed migration stops the deploy.** Right now a failing migration leaves new pods restarting over and over. With the Job, the deploy stops before any new pods start.

**How often this matters:** rarely. Most migrations in the last 6 months took under 5 seconds, and neither setup has a problem with those. But 2 of 41 took over 2 minutes, and both were index builds. Any index build on the orders table can cause this outage again.

**Why not just raise the probe timeouts:** that keeps every slow migration risky. The thresholds would have to be longer than the slowest migration you'll ever run. A pod that really hangs would then also take that long to be noticed and restarted.

**The trade-off:** the old code keeps running for the whole migration, so every migration has to work with the code that's already deployed. Adding an index or a nullable column is fine. Renaming or dropping a column would need two deploys. The Job also needs a deadline long enough for index builds.

I recommend the Job, and I'll set it up as part of this schema change unless you'd rather keep migrations in the pod entrypoint.
