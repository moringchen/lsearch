"""Obsidian-style link graph for knowledge base."""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional
import networkx as nx

from lsearch.config import Config


class LinkGraph:
    """Manages bidirectional link relationships between notes."""

    def __init__(self, config: Config, project_dir: Path | None = None):
        self.config = config
        self.graph_file = Config.get_index_dir(config.name, project_dir) / "link_graph.json"
        self.graph = nx.DiGraph()
        self._load()

    def _load(self) -> None:
        """Load graph from disk."""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
            except Exception:
                self.graph = nx.DiGraph()

    def _save(self) -> None:
        """Save graph to disk."""
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        data = nx.node_link_data(self.graph)
        with open(self.graph_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_note(self, file_path: str, title: str, links: List[str]) -> None:
        """Add or update a note with its outgoing links."""
        # Remove old edges first
        if self.graph.has_node(file_path):
            self.graph.remove_edges_from(list(self.graph.out_edges(file_path)))

        # Add node with metadata
        self.graph.add_node(file_path, title=title)

        # Add edges for each link
        for link in links:
            # Try to resolve the link to a file path
            linked_path = self._resolve_link(file_path, link)
            if linked_path:
                self.graph.add_edge(file_path, linked_path, link_text=link)

        self._save()

    def remove_note(self, file_path: str) -> None:
        """Remove a note from the graph."""
        if self.graph.has_node(file_path):
            self.graph.remove_node(file_path)
            self._save()

    def _resolve_link(self, source_file: str, link: str) -> Optional[str]:
        """Resolve a wiki-link to a file path."""
        source_path = Path(source_file).parent
        base_name = link.split("#")[0].split("|")[0]  # Remove anchor and alias

        # Common markdown extensions
        extensions = [".md", ".markdown", ".mdown"]

        for ext in extensions:
            candidate = source_path / f"{base_name}{ext}"
            if candidate.exists():
                return str(candidate)

        # Try without extension if file exists
            candidate = source_path / base_name
            if candidate.exists():
                return str(candidate)

        return None

    def get_related_notes(self, file_path: str, depth: int = 1) -> List[str]:
        """Get all notes related to the given note (connected by links)."""
        if not self.graph.has_node(file_path):
            return []

        related = set()
        current_level = {file_path}

        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # Add successors (outgoing links)
                next_level.update(self.graph.successors(node))
                # Add predecessors (incoming links / backlinks)
                next_level.update(self.graph.predecessors(node))
            related.update(next_level)
            current_level = next_level

        # Remove the original file
        related.discard(file_path)

        return list(related)

    def get_backlinks(self, file_path: str) -> List[Dict[str, str]]:
        """Get all notes that link to this note."""
        if not self.graph.has_node(file_path):
            return []

        backlinks = []
        for predecessor in self.graph.predecessors(file_path):
            edge_data = self.graph.get_edge_data(predecessor, file_path)
            node_data = self.graph.nodes[predecessor]
            backlinks.append({
                "file_path": predecessor,
                "title": node_data.get("title", ""),
                "link_text": edge_data.get("link_text", "") if edge_data else "",
            })

        return backlinks

    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
        }

    def clear(self) -> None:
        """Clear the entire graph."""
        self.graph.clear()
        if self.graph_file.exists():
            self.graph_file.unlink()
