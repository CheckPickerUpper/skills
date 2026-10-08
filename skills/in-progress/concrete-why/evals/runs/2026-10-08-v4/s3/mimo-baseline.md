It works fine right up until a migration runs long — which already happened. [INC-212](https://acme.atlassian.net/browse/INC-212) is the concrete benefit.

The mechanism: the pod entrypoint runs `migrate deploy` *and* that pod is also under liveness. Your probes kill a pod that hasn't finished in 180s. So any migration over 3 minutes gets its own runner murdered mid-work:

1. Migration `20260914_add_orders_customer_idx` takes 4m10s.
2. Pod 1 holds the advisory lock, gets killed by liveness at 180s.
3. Pods 2 and 3 were waiting on that lock — not serving traffic, not ready.
4. Restart, re-acquire the lock, killed again at 180s. Nothing can finish a 4m10s migration because the execution environment dies at 3m.
5. 19 minutes of orders API downtime, resolved only when someone intervened.

The advisory lock is doing its job correctly — it *guarantees* only one pod migrates. But in the entrypoint that means two replicas are guaranteed to be sitting idle-unready whenever a migration runs, and a long migration is guaranteed to be killed mid-flight. The lock isn't the bug; the liveness probe applying to the migration phase is. They're two mechanisms that are each correct alone and conflict when the migration runs inside a probe-managed container.

The Job fixes it because a Job pod has no readiness/liveness probe killing it at 180s — it runs the migration to completion (4m10s is fine), then the rolling deploy starts pods that only boot the server. Probes now measure what they were meant to measure: server startup, not DDL.

To be fair about the data: 39 of your 41 recent migrations would've been fine either way. The benefit is specifically "slow index builds can't take the API down," which is worth the change because the one time it bit you, it bit for 19 minutes.

If you'd rather keep the entrypoint, the alternative is making the liveness probe tolerate the migration phase — but that re-opens the "server hung past 180s" hole the probe exists for. The Job is the cleaner separation.
