"""BM25 keyword indexer using Whoosh."""

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Term, Or
from whoosh.analysis import StemmingAnalyzer

from lsearch.config import Config


class BM25Indexer:
    """Manages keyword indexing using Whoosh BM25."""

    def __init__(self, config: Config):
        self.config = config
        self.index_dir = Config.get_index_dir(config.name) / "bm25"

        # Define schema
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            file_path=ID(stored=True),
            chunk_index=ID(stored=True),
            title=TEXT(stored=True),
            content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            links=KEYWORD(stored=True, commas=True),
        )

        # Create or open index
        self._ensure_index()

    def _ensure_index(self) -> None:
        """Ensure the index exists."""
        if not self.index_dir.exists():
            self.index_dir.mkdir(parents=True, exist_ok=True)
            self.index = index.create_in(str(self.index_dir), self.schema)
        else:
            self.index = index.open_dir(str(self.index_dir))

    def index_chunks(
        self,
        chunks: List[Dict[str, Any]],
        file_path: str,
    ) -> None:
        """Index a list of text chunks from a file."""
        if not chunks:
            return

        writer = self.index.writer()

        # Delete existing chunks from this file
        writer.delete_by_term("file_path", file_path)

        # Add new chunks
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_path}:{i}"
            links = chunk.get("links", [])
            links_str = ",".join(links) if links else ""

            writer.add_document(
                id=chunk_id,
                file_path=file_path,
                chunk_index=str(i),
                title=chunk.get("title", ""),
                content=chunk["text"],
                links=links_str,
            )

        writer.commit()

    def search(
        self,
        query: str,
        top_k: int = 10,
        file_filter: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search using BM25."""
        with self.index.searcher() as searcher:
            # Parse query for multiple fields
            parser = MultifieldParser(["title", "content"], schema=self.schema)
            q = parser.parse(query)

            # Add file filter if specified
            if file_filter:
                filter_query = Or([Term("file_path", fp) for fp in file_filter])
            else:
                filter_query = None

            results = searcher.search(q, limit=top_k, filter=filter_query)

            formatted = []
            for result in results:
                formatted.append({
                    "id": result["id"],
                    "text": result["content"],
                    "metadata": {
                        "file_path": result["file_path"],
                        "chunk_index": int(result["chunk_index"]),
                        "title": result["title"],
                        "links": result["links"].split(",") if result["links"] else [],
                    },
                    "score": result.score,
                })

            return formatted

    def delete_file(self, file_path: str) -> None:
        """Remove all chunks from a file."""
        writer = self.index.writer()
        writer.delete_by_term("file_path", file_path)
        writer.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        with self.index.searcher() as searcher:
            return {
                "count": searcher.doc_count(),
                "index_dir": str(self.index_dir),
            }

    def clear(self) -> None:
        """Clear the entire index."""
        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)
        self._ensure_index()
