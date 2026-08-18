import collect
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "bloated-repo"


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
