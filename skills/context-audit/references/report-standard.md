# texteff Review Standard v1

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

## Report shape

Five parts, in this order. The prioritized actions are the deliverable;
evidence is the appendix.

1. **Verdict** — one sentence: total tokens, reducible tokens and %, and
   the single most important action.
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
texteff v0.1 · report standard v1 · tokens: <tiktoken | approximate>
```

## Verification labels

Every finding in the evidence appendix carries one label:

- `verified:` followed by the evidence — the file that does not exist, the
  code that contradicts the claim, the second location of the duplicate.
  **Required for every S1 finding.** An S1 claim that cannot be verified is
  reported as S2 with `suspected:` and an explicit note of what to check.
- `suspected:` followed by the reason — allowed for S2/S3 only.

## Learning loop

Each real audit run appends an entry to `docs/audit-learnings.md` in the
texteff repo: date, repo audited, what the standard or taxonomy got wrong
or missed, and what the user overrode. When a lesson repeats across runs,
it graduates into this standard and the version bumps. Do not edit this
standard mid-audit; finish under the current version, record the lesson,
change the standard separately.
