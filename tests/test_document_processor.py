"""Tests for document processor."""

import pytest
import tempfile
from pathlib import Path

from lsearch.config import Config
from lsearch.document_processor import DocumentProcessor


@pytest.fixture
def processor():
    """Create a document processor."""
    config = Config()
    return DocumentProcessor(config)


class TestFrontmatterExtraction:
    """Tests for YAML frontmatter extraction."""

    def test_extract_frontmatter_basic(self, processor):
        """Test basic frontmatter extraction."""
        content = """---
title: Test Document
author: John Doe
---

# Body Content

This is the body.
"""
        frontmatter, body = processor._extract_frontmatter(content)

        assert frontmatter == {"title": "Test Document", "author": "John Doe"}
        assert "# Body Content" in body

    def test_extract_frontmatter_empty(self, processor):
        """Test content without frontmatter."""
        content = "# Just a title\n\nSome content"
        frontmatter, body = processor._extract_frontmatter(content)

        assert frontmatter == {}
        assert body == content

    def test_extract_frontmatter_invalid_yaml(self, processor):
        """Test invalid YAML frontmatter."""
        content = """---
invalid: yaml: :: ::
---

# Body
"""
        frontmatter, body = processor._extract_frontmatter(content)

        # Should return empty frontmatter and full content
        assert frontmatter == {}


class TestTitleExtraction:
    """Tests for title extraction."""

    def test_extract_title_from_h1(self, processor):
        """Test extracting title from H1."""
        content = "# My Document Title\n\nSome content"
        title = processor._extract_title(content)

        assert title == "My Document Title"

    def test_extract_title_no_h1(self, processor):
        """Test content without H1."""
        content = "## Section\n\nSome content"
        title = processor._extract_title(content)

        assert title == ""


class TestWikiLinksExtraction:
    """Tests for wiki-links extraction."""

    def test_extract_wiki_links_basic(self, processor):
        """Test basic wiki-link extraction."""
        content = "This is a [[Wiki Link]] in text."
        links = processor._extract_wiki_links(content)

        assert "Wiki Link" in links

    def test_extract_wiki_links_multiple(self, processor):
        """Test extracting multiple wiki-links."""
        content = "See [[First Link]] and [[Second Link]] for more."
        links = processor._extract_wiki_links(content)

        assert "First Link" in links
        assert "Second Link" in links

    def test_extract_wiki_links_with_alias(self, processor):
        """Test wiki-link with alias."""
        content = "See [[Note Title|Display Text]] for info."
        links = processor._extract_wiki_links(content)

        assert "Note Title" in links
        assert "Display Text" not in links  # Should only extract the link target

    def test_extract_wiki_links_with_anchor(self, processor):
        """Test wiki-link with anchor."""
        content = "See [[Note Title#Section]] for details."
        links = processor._extract_wiki_links(content)

        assert "Note Title" in links
        assert "Section" not in links  # Should only extract the note name


class TestChunking:
    """Tests for text chunking."""

    def test_chunk_text_small(self, processor):
        """Test chunking small text."""
        text = "This is a short text."
        chunks = processor._chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_large(self, processor):
        """Test chunking large text."""
        # Create text larger than chunk_size
        words = ["word" + str(i) for i in range(1000)]
        text = " ".join(words)

        chunks = processor._chunk_text(text)

        # Should have multiple chunks
        assert len(chunks) > 1

    def test_chunk_overlap(self, processor):
        """Test that chunks have overlap."""
        config = Config(chunk_size=100, chunk_overlap=20)
        processor = DocumentProcessor(config)

        words = ["word" + str(i) for i in range(200)]
        text = " ".join(words)

        chunks = processor._chunk_text(text)

        # Check overlap by comparing end of first chunk with start of second
        if len(chunks) > 1:
            first_chunk_words = chunks[0].split()
            second_chunk_words = chunks[1].split()
            # Some words should overlap
            assert any(w in second_chunk_words for w in first_chunk_words[-20:])


class TestShouldIndex:
    """Tests for should_index method."""

    def test_should_index_markdown(self, processor):
        """Test that markdown files should be indexed."""
        assert processor.should_index("/path/to/file.md") is True
        assert processor.should_index("/path/to/file.markdown") is True

    def test_should_index_exclude_patterns(self, processor):
        """Test exclude patterns."""
        assert processor.should_index("/path/node_modules/file.md") is False
        assert processor.should_index("/path/.git/config.md") is False
        assert processor.should_index("/path/__pycache__/readme.md") is False

    def test_should_index_non_markdown(self, processor):
        """Test non-markdown files."""
        assert processor.should_index("/path/to/file.txt") is False
        assert processor.should_index("/path/to/file.py") is False


class TestProcessContent:
    """Tests for process_content method."""

    def test_process_content_full(self, processor):
        """Test processing full content."""
        content = """---
title: My Doc
category: test
---

# Header

This is content with [[Link One]] and [[Link Two]].
"""
        chunks, metadata = processor.process_content(content, "/test/file.md")

        assert metadata["title"] == "My Doc"
        assert "Link One" in metadata["links"]
        assert "Link Two" in metadata["links"]
        assert metadata["file_path"] == "/test/file.md"
        assert len(chunks) > 0

    def test_process_file(self, processor, tmp_path):
        """Test processing a real file."""
        # Create a test file
        test_file = tmp_path / "test.md"
        test_file.write_text("""# Test File

This is a test with [[Link]].
""")

        chunks, metadata = processor.process_file(str(test_file))

        assert metadata["title"] == "Test File"
        assert "Link" in metadata["links"]
