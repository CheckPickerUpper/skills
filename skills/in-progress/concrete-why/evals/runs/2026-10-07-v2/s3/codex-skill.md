The benefit is keeping a long migration from repeatedly restarting all three orders pods. My earlier “cleaner, more robust” wording wasn’t a reason; the recorded outage is.

**[INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212)**: on September 14, an index migration took 4m10s, exceeding the liveness probe’s 180-second limit. All three pods were killed mid-migration, restarted and waited on the lock again. The orders API was down for 19 minutes.

- **With a pre-deploy Job:** the pipeline runs the migration before rolling the server pods. I infer that this removes the restart loop seen in INC-212, because the migration no longer runs inside pods subject to that server liveness probe. Deployment still waits for the migration to finish.
- **With migrations on boot:** Prisma’s lock prevents duplicate application, but the waiting pods still face the restart deadline. A migration exceeding three minutes can hit the same failure again.

Most migrations finish under five seconds, so this adds a separate deployment step with little benefit for those. But two of the last 41 exceeded two minutes, both index builds.

**What decides it:** migration time can exceed the server’s startup deadline. The pipeline already supports a Job before rollout, so I recommend using it. This addresses the observed restart loop; it doesn’t prove the migration itself cannot disrupt database traffic.