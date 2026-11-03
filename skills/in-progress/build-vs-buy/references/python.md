# Python: usual owners to check

Candidates to check, not a verdict. The repository's declared choices and
`pyproject.toml` come first; confirm current APIs and maintenance from primary
sources.

| Need | Usual owner |
| --- | --- |
| Command-line parsing | `argparse` (standard library), `typer` or `click`; use the one the project declares |
| Parsing and validating external data | `pydantic` |
| HTTP client | `httpx` |
| Retries and backoff | `tenacity` |
| Fake time in tests | `time-machine` or `freezegun` |
| Database access and migrations | `SQLAlchemy` and `alembic` |
| Decimal money | `decimal` (standard library) |
| Paths, temporary files, atomic replace | `pathlib`, `tempfile`, `os.replace` (standard library) |
| File digests | `hashlib` (`hashlib.file_digest`) |
| Structured logging | `logging` (standard library) or `structlog` |
| Subprocesses | `subprocess.run` with an argument list, never a shell string |
| Concurrency | `asyncio` task groups or `concurrent.futures` |
