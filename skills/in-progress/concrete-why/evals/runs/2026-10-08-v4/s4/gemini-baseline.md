Leaving them open blocks the v3.2 release. Closing them unblocks it.

- **#402, #403, and #404**: Closing them is correct. They are already resolved (#402 shipped in v2.3, #403 is obsolete because v3.0 requires Android 10, #404 was fixed in PR #470). Leaving them open falsely blocks v3.2.
- **#401 (dark mode flicker)**: I was wrong to suggest closing this. It still reproduces on `main`. Under your rules, every bug must be fixed or explicitly closed as won't-fix by you. Leaving it open correctly blocks v3.2 until you make that decision.
