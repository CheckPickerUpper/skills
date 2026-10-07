The benefit is that a slow migration won’t restart all three API pods and take orders down.

The advisory lock prevents duplicate migrations, but the waiting pods still hit the 180-second liveness limit. That happened in [INC-212](https://acme.atlassian.net/browse/INC-212): the index migration took 4m10s, and the restart cycle caused a 19-minute outage.

A pre-deploy Job runs the migration while the existing pods keep serving, then rolls out the new pods only after it succeeds. Most migrations finish under 5 seconds, so you usually won’t notice a difference. This change addresses the slow ones; “cleaner” wasn’t the useful reason.