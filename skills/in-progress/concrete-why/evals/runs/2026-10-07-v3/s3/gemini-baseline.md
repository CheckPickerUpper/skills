It actually caused the 19-minute outage you had last month (INC-212). 

While it works fine for quick schema changes, Kubernetes is currently configured to kill and restart any pod that isn't healthy within 3 minutes (the 180s liveness probe). Because Prisma migrations run during pod startup, any migration that takes longer than 3 minutes gets killed mid-flight. When the pod restarts, it tries to run the migration again, hits the 3-minute limit again, and enters a crash loop. This is exactly what happened during INC-212 when the customer index build took 4m10s. 

Moving `prisma migrate deploy` to a pre-deploy Job decouples the database migration from the pod's startup lifecycle. The Job can safely take as long as it needs to build an index without getting killed by health checks, and your existing pods will stay up and serve traffic normally until the migration finishes and the new code rolls out.
