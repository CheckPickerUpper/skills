# Rust: usual owners to check

Candidates to check, not a verdict. The repository's declared choices and
`Cargo.toml` come first; confirm current APIs and maintenance on docs.rs and
the crate repository.

| Need | Usual owner |
| --- | --- |
| Command-line parsing | `clap` |
| Serialization | `serde` with `serde_json` or the format's crate |
| HTTP client | `reqwest` |
| HTTP server and middleware, including retries and timeouts | `axum` with `tower` |
| Async runtime and channels | `tokio` |
| Retries and backoff | `backon` or `tower::retry` |
| Database access with checked queries and migrations | `sqlx` |
| Logging and tracing | `tracing` with `tracing-subscriber` |
| Decimal money | `rust_decimal` |
| Dates and times | `jiff`, `chrono` or `time` |
| Error types | `thiserror` for libraries, `anyhow` at the application edge |
| Temporary files and atomic replace | `tempfile` (`NamedTempFile::persist`) |
