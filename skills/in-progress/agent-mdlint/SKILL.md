---
name: agent-mdlint
description: Review AGENTS.md changes for Markdown defects, duplicated or conflicting instructions, and unintended semantic drift. Use when editing or reviewing agent instruction files, especially large rewrites or diffs that remove existing rules.
---

# Agent MD Lint

Review the instruction file as a working contract, not as ordinary prose. Find structural defects and determine whether the change preserves the requested intent and the rules that still apply.

## Review the change

1. Establish the target file, the requested change, and its source of authority. Check whether the file is authored directly or generated from another source; when generated, inspect the owner and review the generated result without editing it as the source.
2. Read the complete before and after versions when available. Compare the diff and account for every removed or materially changed instruction. Do not assume a shorter file is better, or that a deletion was intentional just because the new text says the same topic differently.
3. Check Markdown structure: headings, lists, fences, blockquotes, frontmatter when used, blank lines, stray whitespace, duplicated passages, and text accidentally joined or detached from its intended section.
4. Check semantic integrity: duplicate statements with different meanings, contradictions, vague or untestable rules, lost scope qualifiers, altered permissions, and rules moved under a heading that changes their apparent scope.
5. For each material deletion or change, determine whether the request authorized it and whether the requirement is preserved elsewhere in the authoritative instructions. Report unexplained losses; do not silently restore, invent, or broaden policy.
6. If edits are authorized, correct the instruction file at its canonical source. Then reread the complete result and inspect the final diff for omissions, duplication, and unrelated changes.

## Report

Lead with whether the file is ready to use. For each issue, cite the exact heading or text and state the concrete effect: for example, an operating rule was removed, two statements now conflict, or a paragraph is detached by malformed Markdown. Separate confirmed defects from suggestions. If the diff is unavailable, say that semantic preservation could not be established and review the current file for internal defects only.

Do not turn a specific edit failure into a universal policy. Preserve the source document's existing intent unless the user asked to change it.
