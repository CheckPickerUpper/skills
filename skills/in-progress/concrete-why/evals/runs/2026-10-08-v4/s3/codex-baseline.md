The benefit is that a slow migration won’t keep restarting the API pods. “Cleaner” was too vague.

That happened in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212): the index migration took 4m10s, but liveness restarted each pod after 3 minutes. They restarted and waited on the migration lock again, leaving orders down for 19 minutes. Prisma’s lock prevents duplicate migrations; it doesn’t prevent those restarts.

With a pre-deploy Job, the existing API pods keep serving while the migration runs. The pipeline rolls out the new pods only after it succeeds. That requires the schema change to remain compatible with the running version.

Most migrations finish in under 5 seconds, so you usually won’t notice a difference. I recommend the Job to prevent another outage from the occasional slow index build.