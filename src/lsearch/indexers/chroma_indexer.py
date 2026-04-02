"""ChromaDB vector indexer."""

import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from lsearch.config import Config
from lsearch.embedding import get_embedding_manager


class ChromaIndexer:
    """Manages vector indexing using ChromaDB."""

    def __init__(self, config: Config):
        self.config = config
        self.index_dir = Config.get_index_dir(config.name) / "chroma"
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.index_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        self.embedding = get_embedding_manager(config.embedding_model)

    def _generate_id(self, file_path: str, chunk_index: int) -> str:
        """Generate a unique ID for a document chunk."""
        content = f"{file_path}:{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()

    def index_chunks(
        self,
        chunks: List[Dict[str, Any]],
        file_path: str,
    ) -> None:
        """Index a list of text chunks from a file."""
        if not chunks:
            return

        # Delete existing chunks from this file
        self.delete_file(file_path)

        # Prepare data for indexing
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_id(file_path, i)
            ids.append(chunk_id)
            documents.append(chunk["text"])
            # Build metadata, excluding empty lists (ChromaDB doesn't accept them)
            metadata = {
                "file_path": file_path,
                "chunk_index": i,
                "title": chunk.get("title", ""),
            }
            links = chunk.get("links", [])
            if links:
                metadata["links"] = links
            metadatas.append(metadata)

        # Generate embeddings and add to collection
        embeddings = self.embedding.embed(documents)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        query_embedding = self.embedding.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1.0 - results["distances"][0][i],  # Convert distance to similarity
            })

        return formatted

    def delete_file(self, file_path: str) -> None:
        """Remove all chunks from a file."""
        try:
            self.collection.delete(where={"file_path": file_path})
        except Exception:
            pass  # No chunks from this file

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            "count": self.collection.count(),
            "index_dir": str(self.index_dir),
        }

    def clear(self) -> None:
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            pass
