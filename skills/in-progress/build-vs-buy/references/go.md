# Go: usual owners to check

These are candidates to check, not a verdict. The repository's declared choices
and `go.mod` come first; confirm a candidate's current API, version and
maintenance from its documentation before relying on it.

| Need | Usual owner |
| --- | --- |
| Postgres access, pooling, LISTEN/NOTIFY | `github.com/jackc/pgx/v5` (`pgxpool`; `Conn.WaitForNotification` for notifications) |
| Type-checked SQL | `sqlc` generating code from queries |
| Migrations | `github.com/pressly/goose` or `github.com/golang-migrate/migrate` |
| Background jobs, scheduled and unique work on Postgres | `github.com/riverqueue/river` |
| Retries and backoff | `github.com/cenkalti/backoff` |
| Rate limiting | `golang.org/x/time/rate` |
| Fan-out with cancellation, de-duplicated calls, weighted limits | `golang.org/x/sync` (`errgroup`, `singleflight`, `semaphore`) |
| JWT, JWS, JWE, JWK | `github.com/lestrrat-go/jwx` or `github.com/golang-jwt/jwt` |
| Web push | `github.com/SherClockHolmes/webpush-go` |
| Browser automation | `github.com/chromedp/chromedp` or `github.com/go-rod/rod`; one browser per run, a fresh context per test |
| Result and option values | `github.com/samber/mo` |
| Struct validation | `github.com/go-playground/validator` |
| Decimal money | `github.com/shopspring/decimal` or `github.com/cockroachdb/apd` |
| Fake time and waiting for goroutines in tests | `testing/synctest` (standard library from Go 1.25) |
| Logging | `log/slog` (standard library) |
| Tracing and metrics | `go.opentelemetry.io/otel` with its SDK and exporters |
| HTTP routing | `net/http` `ServeMux` method and path patterns, or `github.com/go-chi/chi` |
| Command-line parsing | `flag` (standard library), `github.com/spf13/cobra` or `github.com/alecthomas/kong` |
| Atomic file replace | `github.com/google/renameio` |
| Loading packages with types; writing and testing analyzers | `golang.org/x/tools/go/packages`, `go/analysis` and `analysistest` |
| Recognizing generated files and build tags | `go/ast` `IsGenerated`, `go/build/constraint` |
| Server-sent events | `net/http` with `http.ResponseController` flushing |
