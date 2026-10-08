Today, each of the three `acme/orders` pods waits for `prisma migrate deploy` before starting its server. A pre-deploy Job lets migrations finish while the existing pods keep serving, then starts the rollout.

My earlier “cleaner, more robust” wording did not explain that benefit.

The concrete failure is recorded in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), from September 14:

1. All three pods started migration deployment. Prisma’s Postgres advisory lock let one apply the migration; the other two waited.
2. The index migration, `20260914_add_orders_customer_idx`, took 4 minutes 10 seconds.
3. The liveness probe restarted pods after 180 seconds of failures—before the migration could finish.
4. All three pods were killed mid-migration, restarted, and waited on the lock again. The orders API was down for 19 minutes.

The lock already prevents duplicate migration execution. Moving migrations does **not** improve that; it removes the migration wait from server startup, where the probe can interrupt it.

The deployment workflow in `.github/workflows/deploy.yml` can run a Kubernetes Job before rolling the orders Deployment. With that ordering, a slow migration delays the rollout; a failed migration stops it before the existing pods are replaced. Most migrations took under five seconds, so the everyday benefit is small. The two index builds out of 41 migrations that exceeded two minutes are the reason to change it.

I recommend the Job for that specific benefit.

I haven’t confirmed whether the new schema remains compatible with the currently running orders server. That must hold for those pods to keep serving during migration. I also don’t have verified source excerpts or line numbers here to show the entrypoint and probe configuration verbatim.

The deciding fact is whether migration duration can exceed the pod’s startup allowance; this service has already had an outage when it did.