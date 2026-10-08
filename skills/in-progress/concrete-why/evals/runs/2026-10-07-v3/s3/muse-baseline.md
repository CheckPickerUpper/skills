It works for the fast case — 39 of 41 migrations were under 5s — but it caused the 19-minute outage in [INC-212 Orders outage during index migration](https://acme.atlassian.net/browse/INC-212).

Today all 3 pods run `migrate deploy` on boot. Prisma's advisory lock means only one applies the migration and the other two wait, but all three are stuck in the entrypoint failing probes. That index migration took 4m10s, longer than the 120s readiness and 180s liveness limits, so Kubernetes killed all three mid-migration and they restarted into the same wait.

A pre-deploy Job in the pipeline runs once to completion with no probes to kill it, then the Deployment rolls with the schema already ready.
