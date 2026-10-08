Today, all three replicas of `acme/orders`, the Kubernetes service serving the orders API, run `prisma migrate deploy` before starting their server. Moving that command into a Job before the rollout keeps a long migration from trapping all three pods in the restart cycle that caused the previous outage.

My earlier “cleaner, more robust pattern” was a label, not a reason.

[INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) records what happened on September 14:

1. The pods started `20260914_add_orders_customer_idx`, the migration adding the orders customer index. Prisma’s Postgres advisory lock allowed one pod to apply it; the other two waited.
2. The index migration took 4 minutes 10 seconds. The liveness probe configured in `deploy/orders.yaml`, the Deployment configuration controlling these API pods, restarted pods after 180 seconds of failures.
3. All three pods were killed mid-migration. They restarted, ran the migration command again, and waited on the lock again.
4. The orders API was down for 19 minutes.

The lock prevents duplicate migration execution. It does not prevent Kubernetes from killing pods while they apply or wait for a migration.

With a separate Job, `.github/workflows/deploy.yml`, the pipeline that deploys orders, runs the migration before rolling the Deployment. Existing API pods can continue serving while the Job runs; replacement pods start their server without waiting for the migration lock. That removes migration duration from the API pods’ startup time.

For most migrations, the benefit is small: most in the last six months finished in under five seconds. But **2 of 41 exceeded two minutes**, both index builds, and one caused the outage above. The extra step is one Job that the pipeline must wait for and stop on failure; the pipeline already supports running it before the rollout.

I haven’t confirmed how long this new migration takes, whether existing orders servers can operate against the changed schema, or what timeout the Job would use. Those checks are needed before configuring this deployment. I also don’t have the previously read source lines here to quote accurately.

The deciding fact is whether migration completion must fit inside an API pod’s restart deadline. A pre-deploy Job removes that deadline from migrations; keeping the existing API available also requires the schema change to work with the running server version.