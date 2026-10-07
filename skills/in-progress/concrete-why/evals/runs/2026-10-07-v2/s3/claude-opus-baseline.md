The benefit is that a slow migration can no longer take the orders API down. For most deploys you won't see any difference.

**Fast migrations behave the same.** 39 of the last 41 migrations finished in under 5 seconds. For those, running them at pod startup works fine. Prisma's advisory lock makes the other two pods wait and skip it, and nothing breaks.

**Slow migrations are the problem, and we've already had an outage from one.** On 2026-09-14, [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) went like this:

- `20260914_add_orders_customer_idx` took 4m10s.
- The migration ran inside the pods, so the health checks still applied. The readiness check marked the pods unready after 120s, and the liveness check killed them after 180s, partway through the migration.
- All three pods restarted, waited on the lock again and got killed again.
- The orders API was down for 19 minutes over a migration that only needed about 4.

Both of the slow migrations in the last 6 months were index builds. That's a common kind of schema change, so it will happen again.

**What a pre-deploy Job changes:**
- **Nothing kills the migration partway through.** The Job has no liveness check, so a 4-minute index build simply takes 4 minutes.
- **The old pods keep serving traffic while it runs.** The Deployment only rolls out after the Job succeeds, so a slow migration delays the deploy instead of causing an outage. This assumes the migration is compatible with the old code, which it already has to be for a rolling deploy.
- **A failed migration stops the pipeline.** `deploy.yml` fails with the Job's logs, instead of pods crash-looping in production.

**The cheaper alternative** is to raise the liveness timeout above the longest migration we expect. That would have prevented INC-212. But it also slows down how quickly Kubernetes catches a pod that has genuinely hung during normal running. And it only works if we can predict how long migrations take, which we can't reliably.

I haven't checked whether this new orders migration is a quick one or an index build. If it's quick, the current setup would probably handle it. I'd still move to the Job now so the next slow migration doesn't cause another INC-212. I'll go ahead with that unless you'd rather just raise the timeout.
