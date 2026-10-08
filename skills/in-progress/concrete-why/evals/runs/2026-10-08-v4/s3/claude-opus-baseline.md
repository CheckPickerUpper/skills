For most deploys you're right, it works. 39 of the last 41 migrations finished in under 5 seconds, and at that speed it doesn't matter where they run. The Job only helps with slow migrations, and a slow one already took the orders API down.

**What happened in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) on 2026-09-14:**

1. Each of the 3 pods runs `prisma migrate deploy` in its entrypoint, so the server can't start until the migration finishes.
2. Prisma takes a Postgres advisory lock, a database lock that lets only one migrator run at a time. So one pod builds the index while the other two wait on the lock. None of the three is serving yet.
3. The migration `20260914_add_orders_customer_idx` needed 4m10s. The liveness probe, the Kubernetes health check that restarts a pod, kills a pod after 180s of failures. It killed all three pods partway through the migration.
4. The pods restarted and waited on the lock again. The API was down for 19 minutes.

**What changes with a pre-deploy Job:**

- The migration runs in its own one-off pod. That pod has no server, so the 180s liveness limit doesn't apply, and a 4-minute index build simply finishes.
- `deploy.yml` updates the Deployment's pods only after the Job succeeds. New pods go straight to starting the server, so a pod's startup time no longer depends on migration time.
- I'd set up the pipeline to stop if the Job fails. A bad migration would then fail the deploy, and the pods would never get stuck in a restart loop.

**The cheaper alternative:** raise the liveness limit, say to 10 minutes. That would have prevented INC-212 too. The downside is that a pod that is actually hung would stay up for 10 minutes before a restart, on every deploy, not only migration deploys. And a migration longer than 10 minutes would hit the same problem again.

I haven't checked yet whether the new orders schema change includes an index build. The two slow migrations in the last six months were both index builds. I'll check before deploying. Either way, I recommend the Job, because it removes the time limit instead of just raising it.

Separately: the Canva and claude.ai Todoist connectors need authorization before I can use them. Authorize claude.ai connectors in your claude.ai connector settings, and other servers through `/mcp` in an interactive session. Nothing here needs them.
