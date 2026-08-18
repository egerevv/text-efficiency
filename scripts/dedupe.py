#!/usr/bin/env python3
"""Find near-duplicate text across an inventory produced by collect.py.

Usage: python3 dedupe.py INVENTORY_JSON [--threshold 0.5]
"""
import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

WORD_RE = re.compile(r"[a-z0-9']+")
SHINGLE_SIZE = 5
MIN_WORDS = 12


def shingles(text):
    words = WORD_RE.findall(text.lower())
    return {" ".join(words[i:i + SHINGLE_SIZE])
            for i in range(len(words) - SHINGLE_SIZE + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_duplicates(items, threshold=0.5):
    sigs = []
    for it in items:
        if len(WORD_RE.findall(it["text"].lower())) >= MIN_WORDS:
            sigs.append((it, shingles(it["text"])))
    pairs = []
    for (a, sig_a), (b, sig_b) in combinations(sigs, 2):
        sim = jaccard(sig_a, sig_b)
        if sim >= threshold:
            pairs.append({
                "a": a["id"], "a_path": a["path"],
                "a_lines": f"{a['start_line']}-{a['end_line']}",
                "b": b["id"], "b_path": b["path"],
                "b_lines": f"{b['start_line']}-{b['end_line']}",
                "similarity": round(sim, 3),
            })
    return sorted(pairs, key=lambda p: -p["similarity"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", help="inventory JSON from collect.py")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args(argv)
    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    pairs = find_duplicates(inventory["items"], args.threshold)
    print(json.dumps(pairs, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
