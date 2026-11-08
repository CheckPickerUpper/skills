---
"checkpickerupper-skills": minor
---

**`to-issues-clearly`** runs a family check before splitting one change across members.

When an issue's fix would be the same change made in each language, client, rule or package, the skill no longer files one checklist line per member. It lists what really differs per member (one data row each) and gives everything else one shared owner, filed as the line that lands first, proved by one test over every member, and recorded under `## Family` in the issue body. A bug already filed against one member points at that shared line.
