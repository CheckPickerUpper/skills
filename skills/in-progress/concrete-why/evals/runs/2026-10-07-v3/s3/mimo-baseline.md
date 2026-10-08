Fair challenge — for the 39 of 41 migrations that finish in under 5 seconds, there's genuinely no benefit. The advisory lock already solves the concurrency problem. The benefit only shows up in the tail, and the tail is what caused INC-212.

The actual issue: migration duration is coupled to pod liveness. When `20260914_add_orders_customer_idx` took 4m10s, it exceeded the 180s liveness threshold, so the probe killed all three pods mid-migration. They restarted, re-waited on the lock, and got killed again — that loop is what turned a 4-minute migration into 19 minutes of downtime. No amount of tuning the probes fixes this cleanly: raise the threshold high enough for index builds and a genuinely hung pod now takes that long to recover too.

A pre-deploy Job breaks that coupling:
- The Job runs once, has no liveness probe racing the migration, and can take 4 minutes without anything killing it.
- The rolling Deployment only starts after the Job succeeds, so pods boot into a schema that's already in place — startup is just startup again.
- A failed migration fails the deploy instead of leaving pods crash-looping against a half-applied schema.

So it's not "the current setup is broken" — it's "the current setup has a failure mode you've already hit once, and the fix costs one Job manifest plus a pipeline step that `.github/workflows/deploy.yml` already supports."

Want me to go ahead with it, or would you rather just bump the liveness threshold and keep it simple?
