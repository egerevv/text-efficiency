#!/usr/bin/env python3
"""Build a JSON inventory of documentation sections and code comments.

Usage: python3 collect.py REPO_PATH [--output FILE]
Stdlib only; tiktoken is used when importable, else tokens ~= chars/4.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "dist", "build",
    "__pycache__", "target", ".next", ".claude-plugin", "vendor",
}
DOC_EXTS = {".md", ".rst", ".txt"}
DOC_ANYWHERE = {"CLAUDE.md", "AGENTS.md"}
DOC_ANYWHERE_PREFIXES = ("readme", "contributing")
MAX_FILE_BYTES = 1_000_000

LINE_MARKERS = {
    ".py": "#", ".rb": "#", ".sh": "#", ".bash": "#", ".zsh": "#",
    ".yml": "#", ".yaml": "#", ".toml": "#",
    ".js": "//", ".jsx": "//", ".ts": "//", ".tsx": "//", ".go": "//",
    ".rs": "//", ".java": "//", ".c": "//", ".h": "//", ".cpp": "//",
    ".hpp": "//", ".cc": "//",
}
BLOCK_EXTS = {".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java",
              ".c", ".h", ".cpp", ".hpp", ".cc"}
BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

MAX_COMMENT_TOKENS_PER_FILE = 2_000
MAX_TOTAL_TOKENS = 150_000


def split_markdown_sections(text):
    """Split markdown into sections at ATX headings.

    Returns [{"heading", "start_line", "end_line", "text"}]; 1-indexed
    lines, preamble before the first heading has heading=None, blank
    sections are dropped.
    """
    lines = text.splitlines()
    raw = []
    current = {"heading": None, "start_line": 1, "lines": []}
    for lineno, line in enumerate(lines, 1):
        m = HEADING_RE.match(line)
        if m:
            raw.append(current)
            current = {"heading": m.group(2).strip(),
                       "start_line": lineno, "lines": [line]}
        else:
            current["lines"].append(line)
    raw.append(current)

    sections = []
    for s in raw:
        body = "\n".join(s["lines"]).strip()
        if not body:
            continue
        sections.append({
            "heading": s["heading"],
            "start_line": s["start_line"],
            "end_line": s["start_line"] + len(s["lines"]) - 1,
            "text": body,
        })
    return sections


def iter_files(root):
    """Yield files under root, skipping SKIP_DIRS and files over 1 MB.

    Walks with os.walk and prunes SKIP_DIRS from dirnames in place so
    skipped trees (.git, node_modules, etc.) are never descended into or
    enumerated, unlike a glob-then-filter approach.
    """
    root = Path(root)
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for filename in sorted(filenames):
            path = Path(dirpath) / filename
            if not path.is_file():
                continue
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            matches.append(path)
    matches.sort(key=lambda p: p.relative_to(root).parts)
    yield from matches


def is_doc_file(path, root):
    """Docs are CLAUDE.md/AGENTS.md anywhere, README*/CONTRIBUTING*
    (case-insensitive) with a doc extension anywhere, plus other
    .md/.rst/.txt files at the repo root or under docs/."""
    rel = path.relative_to(root)
    if path.name in DOC_ANYWHERE:
        return True
    if path.suffix.lower() in DOC_EXTS:
        if path.name.lower().startswith(DOC_ANYWHERE_PREFIXES):
            return True
        return len(rel.parts) == 1 or rel.parts[0] == "docs"
    return False


def extract_comments(text, ext):
    """Return comment blocks {"start_line", "end_line", "text"} for one
    source file. Consecutive line comments merge into one block."""
    blocks = []
    marker = LINE_MARKERS.get(ext)
    if marker:
        current = None
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(marker) and not stripped.startswith("#!"):
                content = stripped[len(marker):].strip()
                if current and lineno == current["end_line"] + 1:
                    current["end_line"] = lineno
                    current["lines"].append(content)
                else:
                    if current:
                        blocks.append(current)
                    current = {"start_line": lineno, "end_line": lineno,
                               "lines": [content]}
        if current:
            blocks.append(current)
    out = [{"start_line": b["start_line"], "end_line": b["end_line"],
            "text": "\n".join(b["lines"]).strip()} for b in blocks]

    if ext in BLOCK_EXTS:
        for m in BLOCK_RE.finditer(text):
            start = text.count("\n", 0, m.start()) + 1
            end = text.count("\n", 0, m.end()) + 1
            body = m.group(0).strip("/*").strip()
            body = re.sub(r"^\s*\*\s?", "", body, flags=re.MULTILINE).strip()
            if body:
                out.append({"start_line": start, "end_line": end,
                            "text": body})
    return sorted([b for b in out if b["text"]],
                  key=lambda b: b["start_line"])


def make_token_counter():
    """Return (count_fn, method). Uses tiktoken when available."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return (lambda t: len(enc.encode(t))), "tiktoken"
    except Exception:
        return (lambda t: max(1, len(t) // 4)), "approximate"


def build_inventory(root):
    root = Path(root).resolve()
    count, method = make_token_counter()
    items, capped_files, skipped_exts = [], [], set()
    doc_files_skipped = []
    next_id = 0
    doc_total = comment_total = comment_included = 0

    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        ext = path.suffix.lower()

        if is_doc_file(path, root):
            if ext == ".md":
                sections = split_markdown_sections(text)
            else:
                body = text.strip()
                sections = ([{"heading": None, "start_line": 1,
                              "end_line": text.count("\n") + 1,
                              "text": body}] if body else [])
            for s in sections:
                tokens = count(s["text"])
                doc_total += tokens
                items.append({"id": next_id, "path": rel,
                              "kind": "doc-section",
                              "heading": s["heading"],
                              "start_line": s["start_line"],
                              "end_line": s["end_line"],
                              "text": s["text"], "tokens": tokens})
                next_id += 1

        elif ext in LINE_MARKERS or ext in BLOCK_EXTS:
            budget = MAX_COMMENT_TOKENS_PER_FILE
            capped = False
            for block in extract_comments(text, ext):
                tokens = count(block["text"])
                comment_total += tokens
                if tokens <= budget:
                    budget -= tokens
                    comment_included += tokens
                    items.append({"id": next_id, "path": rel,
                                  "kind": "comment", "heading": None,
                                  "start_line": block["start_line"],
                                  "end_line": block["end_line"],
                                  "text": block["text"],
                                  "tokens": tokens})
                    next_id += 1
                else:
                    capped = True
            if capped:
                capped_files.append(rel)

        elif ext in DOC_EXTS:
            doc_files_skipped.append(rel)

        elif ext:
            skipped_exts.add(ext)

    global_cap_applied = False
    if doc_total + comment_included > MAX_TOTAL_TOKENS:
        global_cap_applied = True
        kept, budget = [], MAX_TOTAL_TOKENS
        for item in sorted(items, key=lambda i: -i["tokens"]):
            if item["tokens"] <= budget:
                kept.append(item)
                budget -= item["tokens"]
        items = sorted(kept, key=lambda i: i["id"])

    # Compute what's actually included from the final items list
    doc_tokens_included = sum(i["tokens"] for i in items if i["kind"] == "doc-section")
    comment_tokens_included = sum(i["tokens"] for i in items if i["kind"] == "comment")

    return {
        "repo": str(root),
        "token_method": method,
        "items": items,
        "coverage": {
            "doc_tokens": doc_total,
            "doc_tokens_included": doc_tokens_included,
            "comment_tokens_total": comment_total,
            "comment_tokens_included": comment_tokens_included,
            "comment_files_capped": capped_files,
            "global_cap_applied": global_cap_applied,
            "doc_files_skipped": sorted(doc_files_skipped),
        },
        "skipped_extensions": sorted(skipped_exts),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="path to the repository to inventory")
    parser.add_argument("--output", help="write JSON here instead of stdout")
    args = parser.parse_args(argv)
    root = Path(args.repo)
    if not root.is_dir():
        parser.error(f"not a directory: {args.repo}")
    payload = json.dumps(build_inventory(root), indent=1)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"wrote inventory to {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
