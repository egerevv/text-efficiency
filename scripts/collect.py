#!/usr/bin/env python3
"""Build a JSON inventory of documentation sections and code comments.

Usage: python3 collect.py REPO_PATH [--output FILE]
Stdlib only; tiktoken is used when importable, else tokens ~= chars/4.
"""
import re
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "dist", "build",
    "__pycache__", "target", ".next", ".claude-plugin", "vendor",
}
DOC_EXTS = {".md", ".rst", ".txt"}
DOC_ANYWHERE = {"CLAUDE.md", "AGENTS.md"}
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
    """Yield files under root, skipping SKIP_DIRS and files over 1 MB."""
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        yield path


def is_doc_file(path, root):
    """Docs are CLAUDE.md/AGENTS.md anywhere, plus .md/.rst/.txt at the
    repo root or under docs/."""
    rel = path.relative_to(root)
    if path.name in DOC_ANYWHERE:
        return True
    if path.suffix.lower() in DOC_EXTS:
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
