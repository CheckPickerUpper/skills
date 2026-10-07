**Short answer:** The benefit is that a slow migration can no longer take the orders API down. My "cleaner, more robust" wasn't a reason. The concrete one is INC-212, and your schema change is the kind of migration that can repeat it.

**What happens today:** Each of the 3 pods runs `prisma migrate deploy` in its entrypoint before starting the server. Prisma's advisory lock stops them applying a migration twice, so the 2nd and 3rd pods wait on the lock. The migration works as long as it finishes before the probes give up. The readiness probe marks a pod unready after 120s (`failureThreshold: 12 × periodSeconds: 10` in `deploy/orders.yaml`). The liveness probe restarts a pod after 180s of failures.

**What went wrong:** [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), 2026-09-14. Migration `20260914_add_orders_customer_idx` took 4m10s, which is longer than the 180s liveness limit. All three pods were killed mid-migration, restarted, and queued on the lock again. The orders API was down for 19 minutes.

**How often this will happen:** Most migrations in the last 6 months took under 5 seconds, and those are fine as they are. 2 of 41 took over 2 minutes, and both were index builds. That's about 1 in 20, and the incident was one of them. Your own comment that it "works fine now" is true for about 95% of migrations.

- *If we move migrations to a pre-deploy Job:* the deploy pipeline (`.github/workflows/deploy.yml`) runs the migration as a one-off Kubernetes Job before rolling the Deployment. The running pods keep serving on the old schema while it runs. A 4-minute index build then costs a 4-minute-longer deploy, and the probes never see it.
- *If we leave it:* a migration over 180s takes all three pods down at once, because the probes time out a pod that is only waiting or migrating. Each restart waits on the lock again, so the outage lasts as long as the migration plus the restart cycles.

**Cost of the Job:** one new Job manifest and a pipeline step, and a failed migration now fails the deploy before any pods roll. I have not weighed that against a cheaper fix.

**The cheaper alternative:** I haven't checked whether raising the liveness `failureThreshold` above the longest migration would also stop the outage. That would be a one-line change. It has two problems: you'd have to guess the longest future index build, and a pod that is really hung would take just as long to restart. I'd still pick the Job, but if you want the smaller change, that's the option.

**What decides it:** whether the schema change includes an index build or other long operation. If it's a plain column add (under 5s), leave it as is and ship. If it builds an index on `orders`, do the Job first. Do you know which one this change is?
