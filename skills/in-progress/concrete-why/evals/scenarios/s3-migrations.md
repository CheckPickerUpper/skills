# Scenario: migrations on boot vs separate step

## Facts verified earlier in this session
- Service `acme/orders` runs on Kubernetes with 3 replicas. Today each pod runs `prisma migrate deploy` in its entrypoint before starting the server.
- Prisma takes a Postgres advisory lock during `migrate deploy`, so concurrent pods do not apply the same migration twice; the 2nd and 3rd pods wait on the lock.
- The readiness probe in `deploy/orders.yaml` has `failureThreshold: 12, periodSeconds: 10` (pod marked unready after 120s) and the liveness probe restarts a pod after 180s of failures.
- Incident [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), 2026-09-14: migration `20260914_add_orders_customer_idx` took 4m10s. All three pods were killed by the liveness probe mid-migration, restarted, re-waited on the lock; orders API was down 19 minutes.
- Most migrations in the last 6 months took under 5 seconds; 2 of 41 took over 2 minutes (both index builds).
- The deploy pipeline (`.github/workflows/deploy.yml`) can run a one-off Kubernetes Job before rolling the Deployment.

## Conversation so far
**User:** set up the deploy for the new orders schema change
**Assistant:** I'll move migrations out of the pod entrypoint into a pre-deploy Job. It's the cleaner, more robust pattern.
**User:** whats the actual benefit tho it works fine now
