import collect
import json
import subprocess
import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "bloated-repo"
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "collect.py"


def test_split_sections_by_heading():
    text = "# Title\n\nintro text\n\n## Install\n\nrun make\n"
    sections = collect.split_markdown_sections(text)
    assert [s["heading"] for s in sections] == ["Title", "Install"]
    assert sections[0]["start_line"] == 1
    assert sections[1]["start_line"] == 5
    assert "run make" in sections[1]["text"]


def test_preamble_before_first_heading():
    text = "some preamble\n\n# First\nbody\n"
    sections = collect.split_markdown_sections(text)
    assert sections[0]["heading"] is None
    assert "some preamble" in sections[0]["text"]
    assert sections[1]["heading"] == "First"


def test_empty_sections_dropped():
    text = "# A\n\n# B\ncontent\n"
    sections = collect.split_markdown_sections(text)
    # "# A" has a heading line but that still yields text "# A"; only
    # fully blank chunks are dropped
    assert all(s["text"] for s in sections)


def test_iter_files_skips_git_and_big_dirs(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "a.js").write_text("x")
    (tmp_path / "keep.py").write_text("x = 1")
    files = [p.name for p in collect.iter_files(tmp_path)]
    assert files == ["keep.py"]


def test_is_doc_file():
    root = FIXTURE
    assert collect.is_doc_file(root / "README.md", root)
    assert collect.is_doc_file(root / "AGENTS.md", root)
    assert not collect.is_doc_file(root / "src" / "app.py", root)


def test_is_doc_file_nested_readme_and_contributing_anywhere():
    root = Path("/repo")
    assert collect.is_doc_file(root / "pkg" / "README.md", root)
    assert collect.is_doc_file(root / "sub" / "readme.rst", root)
    assert collect.is_doc_file(root / "a" / "b" / "CONTRIBUTING.txt", root)


def test_is_doc_file_markdown_anywhere_but_txt_rst_by_location():
    root = Path("/repo")
    assert collect.is_doc_file(root / "notes" / "ideas.md", root)
    assert collect.is_doc_file(root / "a" / "b" / "deep.md", root)
    assert not collect.is_doc_file(root / "systems" / "requirements.txt", root)
    assert not collect.is_doc_file(root / "pkg" / "notes.rst", root)
    assert collect.is_doc_file(root / "notes.rst", root)
    assert collect.is_doc_file(root / "docs" / "notes.txt", root)


def test_nested_readme_collected(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "README.md").write_text(
        "# Pkg\n\nSome package readme content that is not empty.\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "readme.rst").write_text(
        "Sub readme content goes here.\n")
    inv = collect.build_inventory(tmp_path)
    paths = {i["path"] for i in inv["items"]}
    assert "pkg/README.md" in paths
    assert "sub/readme.rst" in paths


def test_nested_markdown_collected_txt_skipped_and_recorded(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "ideas.md").write_text("# Ideas\n\nSome idea text.\n")
    (tmp_path / "notes" / "data.txt").write_text("Loose text file content.\n")
    inv = collect.build_inventory(tmp_path)
    paths = {i["path"] for i in inv["items"]}
    assert "notes/ideas.md" in paths
    assert "notes/data.txt" not in paths
    assert inv["coverage"]["doc_files_skipped"] == ["notes/data.txt"]


def test_scratch_dirs_never_walked(tmp_path):
    (tmp_path / ".superpowers" / "sdd").mkdir(parents=True)
    (tmp_path / ".superpowers" / "sdd" / "brief.md").write_text("# Brief\n\nScratch.\n")
    (tmp_path / "real.md").write_text("# Real\n\nKept content.\n")
    inv = collect.build_inventory(tmp_path)
    paths = {i["path"] for i in inv["items"]}
    assert paths == {"real.md"}
    assert inv["coverage"]["doc_files_skipped"] == []


def test_extract_python_line_comments():
    text = "x = 1\n# first line\n# second line\ny = 2\n# alone\n"
    blocks = collect.extract_comments(text, ".py")
    assert len(blocks) == 2
    assert blocks[0]["text"] == "first line\nsecond line"
    assert blocks[0]["start_line"] == 2
    assert blocks[0]["end_line"] == 3
    assert blocks[1]["text"] == "alone"


def test_shebang_not_a_comment():
    blocks = collect.extract_comments("#!/usr/bin/env python3\nx = 1\n", ".py")
    assert blocks == []


def test_extract_js_block_comments():
    text = "/*\n * Formats a name.\n */\nfunction f() {\n  // inline note\n}\n"
    blocks = collect.extract_comments(text, ".js")
    texts = [b["text"] for b in blocks]
    assert any("Formats a name." in t for t in texts)
    assert any("inline note" in t for t in texts)
    assert blocks[0]["start_line"] == 1
    assert blocks[0]["end_line"] == 3


def test_token_counter_reports_method():
    counter, method = collect.make_token_counter()
    assert method in ("tiktoken", "approximate")
    assert counter("hello world, this is text") > 0
    assert counter("") >= 0


def test_build_inventory_fixture():
    inv = collect.build_inventory(FIXTURE)
    kinds = {i["kind"] for i in inv["items"]}
    assert kinds == {"doc-section", "comment"}
    paths = {i["path"] for i in inv["items"]}
    assert "README.md" in paths
    assert "AGENTS.md" in paths
    assert "src/app.py" in paths
    assert "src/utils.js" in paths
    ids = [i["id"] for i in inv["items"]]
    assert ids == sorted(set(ids))
    assert inv["coverage"]["comment_tokens_included"] <= \
        inv["coverage"]["comment_tokens_total"]
    assert inv["coverage"]["global_cap_applied"] is False


def test_per_file_comment_cap(tmp_path):
    big = "\n".join(f"# unique filler comment line number {i} with extra "
                    f"words to inflate the token count substantially"
                    for i in range(600))
    (tmp_path / "big.py").write_text(big)
    inv = collect.build_inventory(tmp_path)
    assert inv["coverage"]["comment_tokens_included"] <= \
        collect.MAX_COMMENT_TOKENS_PER_FILE
    assert "big.py" in inv["coverage"]["comment_files_capped"]


def test_cli_outputs_json():
    out = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURE)],
        capture_output=True, text=True, check=True)
    inv = json.loads(out.stdout)
    assert inv["token_method"] in ("tiktoken", "approximate")
    assert len(inv["items"]) > 0


def test_global_cap_recomputes_coverage(tmp_path, monkeypatch):
    (tmp_path / "a.md").write_text("# A\n\n" + "alpha words here " * 50)
    (tmp_path / "b.py").write_text("# " + "beta comment words " * 30)
    monkeypatch.setattr(collect, "MAX_TOTAL_TOKENS", 10)
    inv = collect.build_inventory(tmp_path)
    kept = sum(i["tokens"] for i in inv["items"])
    assert kept <= 10
    cov = inv["coverage"]
    assert cov["global_cap_applied"] is True
    assert cov["doc_tokens_included"] + cov["comment_tokens_included"] == kept
