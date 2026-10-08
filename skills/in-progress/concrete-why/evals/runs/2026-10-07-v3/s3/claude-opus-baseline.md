It works fine for most migrations, but not for slow ones, and that already caused an outage.

**What goes wrong today.** Each pod runs `prisma migrate deploy` before starting the server. Meanwhile, `deploy/orders.yaml` gives each pod a fixed amount of time to come up:

```yaml
readinessProbe:
  periodSeconds: 10
  failureThreshold: 12   # unready after 120s
livenessProbe:
  # restarts the pod after 180s of failures
```

The server doesn't start until the migration finishes, so the probes count the migration time as the pod failing. Any migration over 180 seconds gets the pod killed partway through. That's what happened in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212) on 2026-09-14:

1. `20260914_add_orders_customer_idx` started on pod 1, which took Prisma's database lock.
2. Pods 2 and 3 waited on that lock. None of the three pods was serving traffic.
3. At 180s the liveness probe killed all three. The migration needed 4m10s.
4. The pods restarted and waited on the lock again, and the cycle repeated.
5. The orders API was down for 19 minutes.

**How often this happens.** In the last 6 months, 39 of 41 migrations took under 5 seconds and never came close to the limit. The 2 that took over 2 minutes were both index builds. So the current setup is fine until a migration builds an index, and then it takes the whole API down.

**What the pre-deploy Job changes.** The pipeline (`.github/workflows/deploy.yml`) runs the migration once, as a separate one-off Kubernetes Job, before it rolls out the new pods:

- **Health probes no longer apply to the migration.** A 4-minute index build just takes 4 minutes. Nothing kills it partway through.
- **The old pods keep serving during the migration.** They stay up until the Job finishes, so a slow migration means a slow deploy instead of an outage.
- **A failed migration stops the deploy.** The new pods never roll out, and the old ones stay up. Today a failed migration means pods crash and restart in a loop.

**What it costs.**
- An extra step in the pipeline.
- One rule for writing migrations: old code keeps running against the new schema while the Job runs, so each migration has to work with the current code. Adding a column or an index is fine. Renaming or dropping a column needs two deploys.

For this schema change specifically: if it builds an index on `orders`, it has the same shape as INC-212 and will probably break the current setup. Even if it doesn't, I'd still make the switch now, so the next index build doesn't take the API down again.

Separately: the Canva and claude.ai Todoist connectors need authorization before I can use them. Connect them in your claude.ai connector settings, or with `/mcp` in an interactive session. Neither one is needed for this deploy.
