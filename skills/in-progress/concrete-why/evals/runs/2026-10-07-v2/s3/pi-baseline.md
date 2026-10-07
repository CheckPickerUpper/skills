It works fine until it doesn't — and it already didn't. [INC-212](https://acme.atlassian.net/browse/INC-212) is exactly this setup failing:

- Migration `20260914_add_orders_customer_idx` took 4m10s.
- Your liveness probe kills a pod after 180s of failures. All three pods were mid-migration, killed, restarted, queued on the advisory lock again — and the index build never got to finish in peace. 19 minutes of orders API downtime.

The core problem: running migrations in the pod couples your migration runtime to your probe budgets. Readiness gives you 120s, liveness 180s. Any migration over ~3 minutes is now a guaranteed kill/restart loop under the current config. You got away with it for 39 of 41 migrations because they were sub-5s — the two that weren't are the ones that hurt.

A pre-deploy Job changes the failure model:

1. **Migration runs to completion regardless of duration.** No liveness probe is going to kill a Job mid-index-build. The 2-minute index migrations stop being dangerous.
2. **One actor instead of three.** No lock contention, no 2nd and 3rd pods sitting unready waiting on the lock during rollout.
3. **Failure becomes a deploy stop, not an outage.** If the migration fails, the Job fails and the pipeline halts before the new ReplicaSet rolls — instead of pods crash-looping against a half-migrated schema and serving errors.

The tradeoff: a one-off Job is one more thing in `.github/workflows/deploy.yml`, and you must not let the Deployment roll out before the Job succeeds (a plain pre-deploy step in the workflow handles this). Your pipeline already supports it, so this is ~10 lines of YAML.

Alternative if you want to keep it in the entrypoint: bump `livenessProbe` failure thresholds so 180s > worst-case migration. But that just makes every slow migration silently hold the rollout hostage, and the next 4-minute index build is still three concurrent restarts away.

My call: move it to the Job. The one incident you have is precisely the class this removes.
