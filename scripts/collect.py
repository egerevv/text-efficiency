#!/usr/bin/env python3
"""Build a JSON inventory of documentation sections and code comments.

Usage: python3 collect.py REPO_PATH [--output FILE]
Stdlib only; tiktoken is used when importable, else tokens ~= chars/4.
"""
import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


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
