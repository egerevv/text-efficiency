# text-efficiency

Measure context debt: the repository text (docs, comments, agent instruction
files) that humans and coding agents repeatedly pay to process without
getting value back.

**texteff** is a Claude Code plugin. Its `/texteff:audit` command inventories
your documentation and code comments, classifies each piece of text by
information value, and produces a Context Efficiency Report — what to keep,
consolidate, or delete. It never edits anything.

## Install

In Claude Code:

    /plugin marketplace add <path-or-url-to-this-repo>
    /plugin install texteff@text-efficiency

## Use

    /texteff:audit          # audit the current repo
    /texteff:audit path/    # audit another directory

Output: a summary in chat plus `texteff-report.md` in the audited repo.

## How it judges text

Every doc section and comment is classified as one of: derivable, structural,
constraint, historical, instructional, duplicated, or stale. Constraints are
gold; derivable and stale text is debt. Details:
[the design spec](docs/superpowers/specs/2026-08-18-texteff-plugin-design.md).

## Project background

The strategy memo behind this project: [docs/strategy-memo.md](docs/strategy-memo.md).
