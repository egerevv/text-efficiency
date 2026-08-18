import collect


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
