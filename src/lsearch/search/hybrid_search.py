"""Hybrid search combining vector and BM25 results."""

from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

from lsearch.config import Config
from lsearch.indexers import ChromaIndexer, BM25Indexer, LinkGraph


class HybridSearcher:
    """Combines vector search (Chroma) and keyword search (BM25) using RRF."""

    def __init__(self, config: Config, project_dir: Path | None = None):
        self.config = config
        self.project_dir = project_dir
        self.chroma = ChromaIndexer(config, project_dir)
        self.bm25 = BM25Indexer(config, project_dir)
        self.link_graph = LinkGraph(config, project_dir)
        self.k = 60  # RRF constant

    def search(
        self,
        query: str,
        top_k: int = 10,
        expand_links: bool = True,
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search with link expansion."""
        # Get results from both indices
        vector_results = self.chroma.search(query, top_k=top_k * 2)
        keyword_results = self.bm25.search(query, top_k=top_k * 2)

        # Apply RRF fusion
        fused_results = self._rrf_fusion(vector_results, keyword_results, top_k)

        # Expand with linked notes if enabled
        if expand_links and self.config.auto_expand_links:
            fused_results = self._expand_with_links(fused_results, top_k)

        return fused_results[:top_k]

    def _rrf_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion of two result lists."""
        scores = defaultdict(float)
        metadata_map = {}

        # Score vector results
        for rank, result in enumerate(vector_results):
            doc_id = self._get_doc_id(result)
            scores[doc_id] += 1.0 / (self.k + rank + 1)
            metadata_map[doc_id] = result

        # Score keyword results
        for rank, result in enumerate(keyword_results):
            doc_id = self._get_doc_id(result)
            scores[doc_id] += 1.0 / (self.k + rank + 1)
            if doc_id not in metadata_map:
                metadata_map[doc_id] = result

        # Sort by score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Build final results
        results = []
        for doc_id, score in sorted_docs[:top_k * 2]:
            meta = metadata_map[doc_id]
            results.append({
                "id": doc_id,
                "text": meta["text"],
                "metadata": meta["metadata"],
                "score": score,
                "source": self._determine_source(meta),
            })

        return results

    def _get_doc_id(self, result: Dict[str, Any]) -> str:
        """Generate a consistent document ID from result."""
        meta = result["metadata"]
        return f"{meta['file_path']}:{meta['chunk_index']}"

    def _determine_source(self, result: Dict[str, Any]) -> str:
        """Determine if result came from vector, keyword, or both."""
        # This could be enhanced to track which sources contributed
        return "hybrid"

    def _expand_with_links(
        self,
        results: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Expand results with linked notes."""
        if not results:
            return results

        # Get unique file paths from top results
        primary_files = set()
        for r in results[:5]:  # Only expand from top 5
            primary_files.add(r["metadata"]["file_path"])

        # Find related notes
        related_files = set()
        for file_path in primary_files:
            related = self.link_graph.get_related_notes(file_path, depth=1)
            related_files.update(related)

        # Remove files already in results
        existing_files = {r["metadata"]["file_path"] for r in results}
        new_files = related_files - existing_files

        if not new_files:
            return results

        # Fetch chunks from related files
        # For now, we'll just note them; in a full implementation,
        # we'd fetch and add them with lower scores
        # This is a simplified version

        return results

    def index_file(
        self,
        file_path: str,
        chunks: List[Dict[str, Any]],
        title: str = "",
        links: List[str] = None,
    ) -> None:
        """Index a file in all backends."""
        if links is None:
            links = []

        self.chroma.index_chunks(chunks, file_path)
        self.bm25.index_chunks(chunks, file_path)
        self.link_graph.add_note(file_path, title, links)

    def delete_file(self, file_path: str) -> None:
        """Remove a file from all indices."""
        self.chroma.delete_file(file_path)
        self.bm25.delete_file(file_path)
        self.link_graph.remove_note(file_path)

    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics."""
        return {
            "chroma": self.chroma.get_stats(),
            "bm25": self.bm25.get_stats(),
            "link_graph": self.link_graph.get_stats(),
        }

    def clear(self) -> None:
        """Clear all indices."""
        self.chroma.clear()
        self.bm25.clear()
        self.link_graph.clear()
