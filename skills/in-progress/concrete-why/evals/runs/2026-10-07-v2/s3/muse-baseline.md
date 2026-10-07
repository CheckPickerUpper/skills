For short migrations there is almost no benefit — most of the last 41 took under 5s, and the Postgres advisory lock in `prisma migrate deploy` already stops the 3 pods from double-applying.

The benefit is availability on long migrations. In [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) on 2026-09-14, `20260914_add_orders_customer_idx` took 4m10s. All 3 pods blocked on the lock in their entrypoint, exceeded the liveness limit (180s of failures, readiness marks unready after 120s in `deploy/orders.yaml`), got killed mid-migration, then restarted and re-waited. Orders API was down 19 minutes.

A pre-deploy Job in `.github/workflows/deploy.yml` runs the migration once to completion before the Deployment rolls, so pods only start after the schema is ready — no startup blocking, no probe kills on index builds.
