# texteff v0.1 — Claude Code Plugin Design

Date: 2026-08-18
Status: approved design, pre-implementation

## Problem

Repositories accumulate "context debt": documentation and comments that are
redundant, stale, or derivable from code. Every agent session pays for that
text in tokens, latency, and distraction. There is no tool that measures it.

## Goal

A Claude Code plugin providing `/texteff:audit`: analyze a repository's
documentation and code comments, classify each piece of text by information
value, and produce a Context Efficiency Report with concrete, non-destructive
recommendations.

## Non-goals (v0.1)

- No automatic edits or deletions (`/texteff:suggest` is v0.2+).
- No benchmark harness, hooks, GitHub Action, badge, or MCP server.
- No standalone CLI or API-key usage — Claude Code is the analysis engine.

## Architecture

Claude Code plugin, installable from this repo via a local marketplace.
Claude performs all judgment; Python scripts perform only deterministic work.

```
text-efficiency/
├── .claude-plugin/plugin.json      # plugin manifest
├── .claude-plugin/marketplace.json # local marketplace for installation
├── commands/audit.md               # /texteff:audit entry point
├── skills/context-audit/SKILL.md   # audit methodology + taxonomy
├── scripts/collect.py              # inventory: docs + comments + tokens
├── scripts/dedupe.py               # near-duplicate detection
├── tests/                          # pytest + fixture repo
│   └── fixtures/bloated-repo/      # planted issues for end-to-end checks
└── README.md                       # project README (strategy memo → docs/)
```

## Data flow: /texteff:audit

1. **Collect** (`collect.py`, deterministic). Walk the target repo:
   - Doc files: README*, CLAUDE.md, AGENTS.md, CONTRIBUTING*, docs/**,
     *.md at repo root. Split into sections by heading.
   - Code comments: extracted per source file with per-language regex
     (Python, JS/TS, Go, Rust, Java, C/C++, Ruby, shell to start).
   - Token counts per item: tiktoken when importable, otherwise chars/4
     labeled as "approximate".
   - Output: single JSON inventory (path, kind, span, text, tokens).
2. **Dedupe** (`dedupe.py`, deterministic). Normalized shingle similarity
   across all sections/comments; emit candidate duplicate pairs above a
   threshold so Claude verifies rather than hunts.
3. **Judge** (Claude, guided by the skill). For each inventory item,
   classify by taxonomy:
   1. Derivable — restates what code already says → usually delete
   2. Structural — explains architecture → valuable
   3. Constraint — non-obvious invariant/warning → extremely valuable
   4. Historical — records a decision → potentially valuable
   5. Instructional — how to run/test/deploy → valuable if not duplicated
   6. Duplicated — same info in multiple places → consolidate
   7. Stale — describes behavior that no longer exists → harmful
   Stale/duplicated claims are spot-checked against the actual code before
   being reported.
4. **Report.** Printed in chat and saved to `texteff-report.md` in the
   audited repo: per-file token totals, % likely redundant, findings with
   file:line pointers and taxonomy labels, estimated context reduction,
   and coverage statement.

## Scale handling

`collect.py` caps comment volume per file and total inventory size, and the
report states coverage explicitly (e.g. "analyzed 82% of comment tokens").
Claude prioritizes files with the highest token counts. No silent truncation.

## Error handling

- Not a git repo / empty repo: audit whatever text exists; say so.
- Unsupported languages: skipped and listed in the coverage statement.
- tiktoken absent: fall back to approximation, labeled in the report.
- Scripts fail: the command reports the failure; Claude may proceed with a
  degraded manual audit only if the user asks.

## Testing

- pytest for `collect.py`: extraction correctness per language, section
  splitting, token counting, caps/coverage accounting.
- pytest for `dedupe.py`: planted duplicates found; distinct text not flagged.
- Fixture repo `tests/fixtures/bloated-repo/` with planted derivable
  comments, duplicated sections, and a stale doc reference.
- End-to-end: run `/texteff:audit` against the fixture; the report must
  surface each planted issue.

## Future sequencing (context, not commitments)

v0.2 `/texteff:suggest` + deep cross-check mode → v0.3 benchmark harness →
GitHub Action/badge → MCP server. The plugin is the distribution surface;
the measurement methodology is the center.
