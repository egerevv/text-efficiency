from pathlib import Path

import collect
import dedupe

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "bloated-repo"

INSTALL = ("Run npm install to install dependencies, then copy the env "
           "example file and set the API key variable before starting.")


def item(i, text, path="a.md"):
    return {"id": i, "path": path, "start_line": 1, "end_line": 3,
            "text": text}


def test_duplicate_pair_found():
    pairs = dedupe.find_duplicates(
        [item(0, INSTALL, "README.md"), item(1, INSTALL, "AGENTS.md")])
    assert len(pairs) == 1
    assert pairs[0]["similarity"] == 1.0
    assert pairs[0]["a_path"] == "README.md"
    assert pairs[0]["b_path"] == "AGENTS.md"


def test_distinct_text_not_flagged():
    other = ("The payment worker reads the outbox table and publishes "
             "events to the message queue for downstream consumers.")
    assert dedupe.find_duplicates([item(0, INSTALL), item(1, other)]) == []


def test_short_text_skipped():
    pairs = dedupe.find_duplicates(
        [item(0, "increment count"), item(1, "increment count")])
    assert pairs == []


def test_fixture_readme_agents_duplicate():
    inv = collect.build_inventory(FIXTURE)
    pairs = dedupe.find_duplicates(inv["items"])
    endpoints = {frozenset((p["a_path"], p["b_path"])) for p in pairs}
    assert frozenset(("README.md", "AGENTS.md")) in endpoints
