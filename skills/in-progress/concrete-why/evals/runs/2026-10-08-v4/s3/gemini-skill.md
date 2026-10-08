I used "cleaner" and "more robust" as labels; they were not reasons. Running migrations in the pod entrypoint means Kubernetes kills the pod if the migration takes longer than the liveness probe's limit; moving it to a pre-deploy Job lets long migrations finish before the new pods start.

**How migrations run today**

Service `acme/orders` serves the orders API and runs on Kubernetes with 3 replicas. Today each pod runs `prisma migrate deploy`—the command that applies database schema changes—in its entrypoint before starting the server. Prisma takes a Postgres advisory lock during the run, so the first pod locks it and the other two wait.

**What goes wrong on long migrations**

`deploy/orders.yaml` is the Kubernetes configuration for the orders pods. It defines when Kubernetes considers the pod stuck and kills it:

```yaml
// deploy/orders.yaml (illustration, not the real code)
livenessProbe:
// ...
// ▸ Kubernetes restarts a pod after 180s of failures.
```

In incident [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212), adding an index took 4m10s.
1. All three pods start and run `prisma migrate deploy`.
2. Pod 1 gets the lock and begins the 4m10s index build. Pods 2 and 3 wait.
3. At 180s, the liveness probe kills all three pods because the server hasn't started.
4. The pods restart, try to migrate again, and re-wait on the lock.
5. Callers of the orders API saw downtime for 19 minutes.

Most migrations take under 5 seconds, but 2 of 41 in the last 6 months took over 2 minutes.

**What the Job changes**

`.github/workflows/deploy.yml` is the deploy pipeline that releases new code. It can run a one-off Kubernetes Job before rolling the Deployment. A Job has no liveness probe, so a 5-minute index build finishes successfully, and then the 3 pods boot and start the server without running migrations themselves.

**What decides it:** can a migration take longer than a pod is allowed to boot? A pre-deploy Job can; a pod entrypoint cannot.
