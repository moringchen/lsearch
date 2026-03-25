"""Document processing and chunking."""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import yaml

from lsearch.config import Config


class DocumentProcessor:
    """Process markdown documents into chunks."""

    def __init__(self, config: Config):
        self.config = config

    def process_file(self, file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process a file into chunks.

        Returns:
            (chunks, metadata)
        """
        path = Path(file_path)

        if not path.exists():
            return [], {}

        # Read file
        content = path.read_text(encoding="utf-8")

        # Parse markdown
        return self.process_content(content, file_path)

    def process_content(
        self,
        content: str,
        file_path: str = "",
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Process markdown content into chunks."""
        # Extract frontmatter
        frontmatter, body = self._extract_frontmatter(content)

        # Extract title
        title = frontmatter.get("title", "")
        if not title:
            title = self._extract_title(body)

        # Extract wiki-links
        links = self._extract_wiki_links(body)

        # Split into chunks
        chunks = self._chunk_text(body)

        # Build chunk objects
        chunk_objects = []
        for i, chunk_text in enumerate(chunks):
            chunk_objects.append({
                "text": chunk_text,
                "title": title,
                "links": links,
                "chunk_index": i,
            })

        metadata = {
            "title": title,
            "links": links,
            "file_path": file_path,
            "frontmatter": frontmatter,
        }

        return chunk_objects, metadata

    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter from markdown."""
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1)) or {}
                body = content[match.end():]
                return frontmatter, body
            except yaml.YAMLError:
                pass

        return {}, content

    def _extract_title(self, content: str) -> str:
        """Extract title from first H1 heading."""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_wiki_links(self, content: str) -> List[str]:
        """Extract Obsidian-style wiki-links [[Like This]]."""
        pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(pattern, content)

        # Clean up links (remove anchors and aliases)
        links = []
        for match in matches:
            # Remove anchor: [[Note#Heading]] -> Note
            # Remove alias: [[Note|Alias]] -> Note
            link = match.split("#")[0].split("|")[0].strip()
            if link:
                links.append(link)

        return list(set(links))  # Deduplicate

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap

        # Simple word-based chunking
        words = text.split()

        if len(words) <= chunk_size:
            return [text]

        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
            i += chunk_size - overlap

        return chunks

    def should_index(self, file_path: str) -> bool:
        """Check if file should be indexed based on exclude patterns."""
        import fnmatch

        path = Path(file_path)

        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(str(path), pattern):
                return False
            if fnmatch.fnmatch(path.name, pattern):
                return False

        # Only index markdown files for now
        if path.suffix.lower() not in ['.md', '.markdown', '.mdown']:
            return False

        return True
