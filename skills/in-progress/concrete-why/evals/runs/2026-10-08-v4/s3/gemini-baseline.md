It caused the 19-minute orders outage last month (INC-212).

Because migrations run during pod startup, they are timed against the pod's 180-second liveness probe timeout. If a migration takes longer than 3 minutes—like the `20260914_add_orders_customer_idx` index build, which took 4m10s—Kubernetes kills all three pods mid-migration. The pods restart, try to migrate again, hit the 180-second timeout again, and fail in a loop.

Running the migration in a pre-deploy Job detaches it from the pod lifecycle. The migration can take as long as it needs, and Kubernetes will wait for it to finish before rolling the new pods.
