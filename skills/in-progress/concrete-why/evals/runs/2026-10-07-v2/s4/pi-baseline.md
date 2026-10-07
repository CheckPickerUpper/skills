Closing does three concrete things on GitHub:

1. **Removes it from the open queue** — anything filtering `is:open` (triage views, open counts, sweeps) stops showing it, so nobody treats it as actionable work anymore.
2. **Drops the milestone's open count** — and here that's the real one: "v3.2" is your release gate, and the release is blocked while *any* issue in it is open. So leaving these four open keeps v3.2 blocked; closing them is what unblocks it.
3. **Records a terminal decision** — per your standing rule, a bug ends fixed or closed as won't-fix by your call. Open is not an allowed resting state.

Nothing is deleted — issue, comments, and links stay readable and it can be reopened.

So the honest answer to "why not leave them open": the only real cost is #2. If you don't mind v3.2 staying blocked, leaving them open costs nothing else.

But I have to correct my own plan: I said "close as stale," and stale is not a valid reason under your rule. Each one needs its actual state:

- **#402** — fixed, shipped in v2.3 by #455 (which just never linked it). Close as completed.
- **#404** — fixed by #470. Close as completed.
- **#403** — the crash was never fixed; v3.0 made it moot by raising `minSdkVersion` to 29 so Android 9 can't install. That's a won't-fix, and it needs your decision, not mine.
- **#401** — this one isn't stale at all: I reproduced the ~150ms white flash on `main` today. It's a live bug. I won't close it without your explicit won't-fix call.

Want me to close #402 and #404 as fixed now, and leave #401 and #403 for your call?
