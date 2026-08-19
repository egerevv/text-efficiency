# Audit learnings

One entry per real audit run: what the standard or taxonomy got wrong or
missed, and what the user overrode. Repeated lessons graduate into
`skills/context-audit/references/report-standard.md` and bump its version.

## 2026-08-19 — notes-business, Verbose-lens pass (first v1.3 run)

- User feedback drove v1.3: reports should weigh text *quality* (where
  summarizing only benefits), not just text existence. Added the Verbose
  type with the proof-of-compression rule.
- First run validated the lossless discipline in both directions: the
  largest kept section (826 tokens of dense notes) correctly did NOT
  flag — every bullet held unique facts/attributions; the real catch was
  contribution-log cells restating their link targets (187 → 86 tokens
  demonstrated, 53%).
- Observation: most Verbose catches so far are really Duplicated-with-
  extra-words (restating a canonical home). Pure verbosity — wordy text
  with one home — hasn't appeared yet in these two repos. Watch whether
  Verbose earns its place as a separate type or folds into Duplicated.
- The report template needs a stated policy for score-neutral updates:
  re-issuing under a newer standard changed reducible tokens (80.0k →
  81.4k) but not the rounded score.

## 2026-08-19 — notes-business (second dogfood, first standard-v1.1 report)

- The root+docs/ location rule missed ~110 nested .md files — the entire
  content of a notes repo. Second occurrence (school_game story/ was the
  first) → graduated immediately: collect.py now collects .md anywhere
  (.rst/.txt keep the location rule to exclude requirements.txt-style
  noise). Shipped mid-session as commit 3b6e08b.
- The 150k global cap silently degraded dedupe: duplicate pairs found in
  a pre-cap partial run vanished once the cap trimmed small sections.
  The cap keeps largest-first, and duplicates are usually small. v0.2:
  run dedupe on the full inventory BEFORE the trim, or exempt items that
  appear in a pair.
- New content class with no taxonomy home: machine-generated run
  artifacts committed in-tree (64k tokens of systems/*/outputs/). Filed
  under Historical, but "Generated" may deserve its own taxonomy type
  with default action "gitignore".
- First score issued (6.5/10). The root-cause clustering rule worked:
  three stale files sharing one cause (layout drift) cost 1.5 once, not
  4.5 — without it the score would have punished the same mistake three
  times.
- Executed SDD plans left in-tree: third occurrence across two repos.
  Pattern is confirmed, not coincidence.

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
