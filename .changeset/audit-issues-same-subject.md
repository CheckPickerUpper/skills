---
"checkpickerupper-skills": patch
---

audit-issues: `audit_issues.py draft` also catches a duplicate written in plain words. It refuses a draft whose title shares rare words with an open issue's title (worth as much as two words no other open title has), lists the three closest titles to read before filing, and its passing message now says exactly what it checked.
