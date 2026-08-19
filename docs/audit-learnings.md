# Audit learnings

One entry per real audit run: what the standard or taxonomy got wrong or
missed, and what the user overrode. Repeated lessons graduate into
`skills/context-audit/references/report-standard.md` and bump its version.

## 2026-08-19 — school_game (first dogfood, pre-standard)

- The report led with taxonomy findings; the user rejected that and asked
  for a harm-ranked, actionable priority list with effort per item.
  → Graduated immediately into report standard v1 (five-part shape,
  prioritized actions first).
- Harm and size diverged completely: the most harmful finding (~1.7k
  tokens of stale README describing a deleted product) was 2% of the
  reducible total; the largest (79k tokens of executed plans) misled
  nobody. → Graduated: severity model ranks S1 Misleading above
  everything regardless of size.
- The location rule (root + docs/ only) silently excluded `story/*.md` —
  real content docs. `doc_files_skipped` coverage caught it, but v0.2
  should consider collecting `*.md` anywhere with a skip-list.
- Dedupe (shingle similarity) found 1 pair; the repo's real cross-file
  problem was *contradiction* (README vs CLAUDE.md disagreeing about a
  deleted feature). Contradiction detection is not in v0.1's pipeline at
  all — strongest candidate for the v0.2 deep cross-check mode.
- Approximate token counts (tiktoken absent) were fine for ranking but
  forced caveats on every number; bundle or document a real tokenizer
  path before any score/badge feature.
