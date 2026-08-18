---
description: Audit a repository for context debt (redundant, stale, low-value text)
argument-hint: [path]
---

Audit the repository at `$ARGUMENTS` for context debt. If no path was
given, audit the current working directory.

Use the context-audit skill from the texteff plugin and follow its
pipeline exactly: collect, dedupe, judge, report.
