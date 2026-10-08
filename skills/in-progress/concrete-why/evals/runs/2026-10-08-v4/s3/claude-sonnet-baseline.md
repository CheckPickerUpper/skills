It works fine for most migrations. In the last 6 months, 39 of 41 took under 5 seconds. The benefit only shows up on the slow ones, and [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) is what one looked like.

On 2026-09-14, `20260914_add_orders_customer_idx` took 4m10s (250s). Liveness restarts a pod after 180s of failures, so this is what happened:

1. All three pods started and ran `prisma migrate deploy`. One took the Postgres advisory lock and began the index build. The other two waited on the lock.
2. The server hadn't started yet, so the probes failed. At 180s the liveness probe killed all three pods, the one holding the lock included.
3. The pods restarted and went back to waiting on the lock, and the orders API stayed down for 19 minutes.

With a pre-deploy Job, the migration isn't subject to the pod's probes, so a 250s build just finishes. The Deployment rolls only after the Job succeeds, so the running pods keep serving while it works. Both slow migrations in the last 6 months were index builds, and `deploy.yml` can already run a one-off Job, so this doesn't need new infrastructure.

There's a cheaper alternative: raise the liveness `failureThreshold` above your longest expected migration. That has a real cost. A genuinely hung server then takes much longer to be restarted, and every pod still sits unready for the whole migration. I'd still do the Job, but the threshold change would also stop a repeat of INC-212.

I haven't checked whether this schema change includes an index build. If it's a small column add, it will take about 5 seconds, and nothing breaks if you ship it as is. I'd still move migrations to the Job before the next index change, because that's the case that took orders down.
