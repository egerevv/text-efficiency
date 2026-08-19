---
name: context-audit
description: Audit a repository's documentation and code comments for context debt — redundant, stale, duplicated, or derivable text. Use when the user runs /texteff:audit or asks to measure documentation bloat, comment quality, or context debt.
---

# Context Audit

Measure which repository text earns its tokens and which is context debt.
This audit only reports — NEVER edit or delete anything in the audited
repo. The only file you may write there is `texteff-report.md`.

## Pipeline

Let TARGET be the directory to audit (default: current working directory).
Let `<scratch>` be the session scratchpad directory when one exists,
otherwise /tmp.

1. **Collect.** Run:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/collect.py" TARGET --output <scratch>/texteff-inventory.json
   ```

2. **Dedupe.** Run:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/dedupe.py" <scratch>/texteff-inventory.json --output <scratch>/texteff-pairs.json
   ```

3. **Judge.** Read both `<scratch>/texteff-inventory.json` and
   `<scratch>/texteff-pairs.json`. Work through items in descending
   token order — the biggest items matter most. Classify EVERY doc
   section, and every comment block you can, using the taxonomy below.
   Rules:
   - Confirm every dedupe pair by reading both texts before reporting
     it as Duplicated.
   - Before labeling anything Stale, verify against the code: if a doc
     mentions a file, check the file exists; if it describes behavior,
     read the relevant code. Never report Stale on suspicion alone.
   - A comment that restates the adjacent identifiers or an obvious
     implementation is Derivable. When unsure whether a comment is
     Derivable or Constraint, read the code around it.
   - Verbose is judged on text that passes every other check: flag it
     ONLY when compression is lossless — every fact, constraint, and
     nuance preserved (losing color is fine; losing information is not).
     If you cannot preserve everything, the text is not Verbose — leave
     it alone. A Verbose finding is never asserted, only demonstrated:
     write the actual compressed rewrite (for long sections, a
     representative excerpt) with before/after token counts. No
     demonstration, no finding. Prioritize the highest-token kept
     sections for this check.
   - If the inventory shows capped files (`coverage.comment_files_capped`) or `coverage.global_cap_applied` is true,
     analyze what is included and state coverage honestly.
   - If `coverage.doc_files_skipped` is non-empty, mention those paths in
     the report's coverage statement as doc files not analyzed.

4. **Report.** Read `${CLAUDE_PLUGIN_ROOT}/skills/context-audit/references/report-standard.md`
   and write `texteff-report.md` into TARGET following it exactly:
   severity model (S1 Misleading / S2 Diluting / S3 Polish, ranked by
   harm, never size), the five-part shape (verdict → prioritized actions
   → leave alone → evidence appendix → coverage), and verification
   labels (`verified:` mandatory for S1). Give the user a short summary
   in chat: the verdict line plus the top 3 actions.

5. **Learn.** After the user has seen the report, append what the audit
   got wrong or the user overrode to `docs/audit-learnings.md` in the
   texteff repo (see the standard's Learning loop section). Skip if
   nothing was learned.

## Taxonomy

| Type | Meaning | Default action |
|---|---|---|
| Derivable | Restates what the code already says | Delete |
| Structural | Explains architecture or component relationships | Keep |
| Constraint | Non-obvious invariant, warning, or requirement | Keep (gold) |
| Historical | Records why a decision was made | Keep if still relevant |
| Instructional | How to run/test/deploy | Keep once; dedupe elsewhere |
| Duplicated | Same information in more than one place | Consolidate to one home |
| Stale | Describes behavior or files that no longer exist | Delete or fix (harmful) |
| Verbose | Full information content survives at materially fewer tokens | Compress (losslessly) |

## Report format

The report's structure, severity model, and evidence rules live in
[references/report-standard.md](references/report-standard.md) — read it
before writing the report. Non-negotiables it enforces: prioritized
actions come before evidence; harm outranks size; every S1 (Misleading)
finding carries `verified:` evidence; a "Leave alone" section names what
is good so nobody over-cleans. Include file:line references exactly as in
the inventory so they are clickable. Do not pad the report — a repo with
little debt gets a short report saying so.
