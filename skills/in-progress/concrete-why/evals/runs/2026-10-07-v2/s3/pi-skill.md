<what-to-do>
**Short answer:** The benefit is only for long migrations: the migration runs in a process Kubernetes won't kill. For the 39 fast migrations of the last 6 months, nothing changes — today's setup is fine there. It still beats the cost.

**What the change buys**
- *If migrations stay in the pod entrypoint:* any migration longer than the 180s liveness limit in `deploy/orders.yaml` (the file holding the probe timings — liveness restarts a pod after 180s of failures) gets its own runner killed mid-apply. The pod restarts, re-waits on the advisory lock behind the other pods, and repeats. That's not hypothetical: [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) (2026-09-14, orders API down 19 minutes) happened exactly this way — migration `20260914_add_orders_customer_idx` took 4m10s, all 3 replicas were killed mid-migration, and the restart loop stretched it to 19 minutes.
- *If migrations run as a one-off Job first (`.github/workflows/deploy.yml`, the deploy pipeline, can already do this):* the migration process has no liveness probe, so a 4-minute index build just takes 4 minutes. Pods start only after it finishes, and none of them can be restarted for being slow during a migration.
- *What it costs:* one Job step in `deploy.yml`, and deploys get slower by the migration's duration because the Deployment rolls after the Job. If the Job fails, the deploy stops before any pod changes — on the current setup the same failure surfaces as pods crash-looping.

**How often this bites:** 2 of the last 41 migrations took over 2 minutes (both index builds) — so roughly 1 deploy in 20 is exposed to the INC-212 failure mode today, and schema changes with indexes are exactly the new orders work landing now.

**What decides it:** whether a migration can run longer than the 180s liveness limit while a pod is its runner. If yes, the pod gets killed mid-migration; a Job doesn't. For sub-minute migrations the answer is no, and there the change buys nothing — it's insurance for the other 2-in-41.
</what-to-do>
