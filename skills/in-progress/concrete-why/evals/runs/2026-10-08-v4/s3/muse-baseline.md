It does for fast ones — 39 of the last 41 migrations were under 5s.

The problem is the slow ones: all 3 pods run `prisma migrate deploy` in the entrypoint, pods 2-3 block on the Postgres advisory lock, go unready after 120s (`failureThreshold: 12, periodSeconds: 10`), then get killed by the liveness probe after 180s.

That's [INC-212](https://acme.atlassian.net/browse/INC-212) on 2026-09-14: `20260914_add_orders_customer_idx` took 4m10s, all 3 pods were killed mid-migration and restart-looped, orders was down 19 min.

A pre-deploy Job in `deploy.yml` runs once before the rollout with no probes, so a 2min+ index build just delays the deploy instead of taking orders down.
