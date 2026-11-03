# TypeScript and React: usual owners to check

Candidates to check, not a verdict. The repository's declared choices and
`package.json` come first; confirm current APIs and maintenance from primary
sources.

## React apps

| Need | Usual owner | What hand-rolling breaks |
| --- | --- | --- |
| Server reads and writes | `@tanstack/react-query` | caching, de-duplication, refetch on focus, retry, stale time, optimistic updates, invalidation |
| Form state | `react-hook-form` | validation, touched and dirty state, the submit lifecycle |
| Parsing external JSON (HTTP, storage, `postMessage`) | `zod` or `valibot` | an untyped value treated as typed |
| Dates | `date-fns` or `dayjs`; never `moment` (maintenance mode) | formatting, parsing and arithmetic that disagree between wire and screen |
| Error reporting | `@sentry/react` (or `@sentry/browser`, `@sentry/nextjs`) | errors that vanish into `console.error` |
| Conditional class names | `clsx` or `classnames` | falsy values and ordering |
| State in the URL | `nuqs` | hand-synced search parameters |
| Dialogs, popovers, tooltips, menus | the component library the project already depends on | focus trapping, escape handling, accessibility |

Tokens, secrets and passwords never go in `localStorage` or `sessionStorage`,
which any injected script can read; they belong in `HttpOnly`, `Secure`
cookies.

## Node and general TypeScript

| Need | Usual owner |
| --- | --- |
| HTTP client | built-in `fetch`, `undici`, or `ky`; never the deprecated `request` |
| Retries and concurrency limits | `p-retry`, `p-limit` |
| Command-line parsing | `commander` or `yargs` |
| Decimal money | `dinero.js`, `big.js` or `decimal.js` |
| Logging | `pino` |
| Fake time in tests | the runner's fake timers (`vi.useFakeTimers`, `jest.useFakeTimers`) |
| HTTP at the test boundary | `msw` |
| Browser automation | `playwright` |

## Standard-library collection shapes

| Hand-rolled | Use |
| --- | --- |
| loop with a seen-set to keep unique values | `[...new Set(items)]` |
| loop with a seen-set keyed on a field | `[...new Map(items.map((item) => [item.key, item])).values()]` |
| loop copying entries into a new `Map` or `Set` | `new Map(source)`, `new Set(source)` |
| an array literal of three or more spreads | `[a, b, c].flat()` |
