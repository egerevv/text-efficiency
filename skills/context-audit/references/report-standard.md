# texteff Review Standard v1.3

How a context audit presents its results. The taxonomy (in SKILL.md) is the
analysis method; this standard is the deliverable's contract. Reports stamp
themselves with this standard's version so old reports stay interpretable
as it evolves.

The severity model and report shape are written to generalize to other
review kinds (code review, doc review); the coverage and evidence rules are
texteff-specific.

## Severity model

Severity measures harm to a reader (human or agent) who trusts the text —
never token count, never category.

| Level | Name | Definition | Examples |
|---|---|---|---|
| S1 | Misleading | Contradicts the code or reality; a reader acting on it does the wrong thing | Stale claims, references to deleted files, wrong instructions |
| S2 | Diluting | True but crowds context: every reader pays for it, few benefit | Executed plans kept in-tree, duplicated sections, derivable comments |
| S3 | Polish | Drifts or grates but misleads no one | Hard-coded counts, style inconsistency, minor redundancy |

Rules:
- S1 items always rank above S2, and S2 above S3, regardless of size.
  A 50-token lie outranks 50,000 tokens of archive.
- Taxonomy → typical severity: Stale → S1; Duplicated, Historical,
  Derivable → S2; count drift and style → S3. Constraint and Structural
  text is not debt — it appears only under "Leave alone".
- Within a level, rank by tokens saved per unit of effort.

## Score

Every score in a report is out of 10 — components and total alike, one
unified scale. Shown in the verdict with its arithmetic. Two components:

- **Accuracy (0–10).** Start at 10; subtract 3 per verified S1 *root
  cause* (a cluster of findings sharing one cause — e.g. four stale
  README sections all describing one deleted feature — counts once).
  Floor 0. Unverified suspicions never reduce Accuracy.
- **Efficiency (0–10).** `10 × (total tokens − reducible tokens) /
  total tokens`, where reducible sums the S2/S3 evidence-appendix
  findings.

Score = the average of the two, rounded to the nearest 0.5. Show all
three numbers: `Score: 6.5/10 (Accuracy 7/10 — one verified S1 root
cause; Efficiency 5.8/10 — 42% reducible)`. The score measures the
text, not the code or the project's worth — say so when a low score
lands on a good codebase.

## Report shape

Five parts, in this order. The prioritized actions are the deliverable;
evidence is the appendix.

1. **Verdict** — one sentence: total tokens, reducible tokens and %,
   the score with its arithmetic, and the single most important action.
2. **Prioritized actions** — a numbered, harm-ranked list. Each item:
   the action (imperative), why now (the harm), and an effort estimate.
   Number items across severity levels in one sequence.
3. **Leave alone** — what was examined and judged good, by name, with one
   line on why. This bounds the work and forbids over-cleaning. A report
   without this section invites deleting the Constraint gold.
4. **Evidence appendix** — the taxonomy findings backing each action:
   `path:start-end — Type — severity`, a short quote, justification, and
   a verification label (below).
5. **Coverage & limitations** — token-count method (tiktoken vs
   approximate), comment-token coverage %, capped files,
   `doc_files_skipped` paths, and anything the audit could not judge.

Header stamp, verbatim shape:

```
# Context Efficiency Report — <repo name>
texteff v0.1 · report standard v1.3 · tokens: <tiktoken | approximate>
```

## Verbose findings (proof-of-compression)

A Verbose finding claims the same information fits in materially fewer
tokens. It is only reportable with a demonstration:

- The evidence appendix entry MUST contain the compressed rewrite (for a
  long section, a representative excerpt rewritten) and before/after
  token counts. An asserted ratio with no rewrite is not a finding.
- The rewrite must be lossless: every fact, constraint, and nuance of the
  original preserved. Style, voice, and color may be lost; information
  may not. Text that only compresses lossily is not Verbose.
- Demonstrated savings join the reducible-token total, so the Efficiency
  component prices them — there is no separate quality score.
- Severity: S3 by default; S2 when one section or file wastes thousands
  of tokens. Prioritized-action entries state the arithmetic and the
  effort to accept: "Compress X: 900 → 250 tokens, rewrite provided."
- Extrapolation must be labeled: if the demonstration covers an excerpt,
  the projected whole-file saving is an estimate — say so.

## Verification labels

Every finding in the evidence appendix carries one label:

- `verified:` followed by the evidence — the file that does not exist, the
  code that contradicts the claim, the second location of the duplicate.
  **Required for every S1 finding.** An S1 claim that cannot be verified is
  reported as S2 with `suspected:` and an explicit note of what to check.
- `suspected:` followed by the reason — allowed for S2/S3 only.

## Changelog

- **v1.3** (2026-08-19): added Verbose findings — lossless-compression
  opportunities, reportable only with a demonstrated rewrite and
  before/after counts; savings feed Efficiency. (User feedback: reports
  should weigh text quality, not just text existence.)
- **v1.2** (2026-08-19): unified scale — Accuracy and Efficiency are each
  0–10 (S1 root cause −3; Efficiency ×10); total is their average.
  Equivalent arithmetic to v1.1, uniform units.
- **v1.1** (2026-08-19): added the Score section (Accuracy + Efficiency,
  each 0–5 summing to /10); verdict now includes it.
- **v1** (2026-08-19): initial — severity model, five-part shape,
  verification labels, learning loop.

## Learning loop

Each real audit run appends an entry to `docs/audit-learnings.md` in the
texteff repo: date, repo audited, what the standard or taxonomy got wrong
or missed, and what the user overrode. When a lesson repeats across runs,
it graduates into this standard and the version bumps. Do not edit this
standard mid-audit; finish under the current version, record the lesson,
change the standard separately.
