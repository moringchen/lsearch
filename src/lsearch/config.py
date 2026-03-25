"""Configuration management for lsearch."""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class PathConfig:
    """Configuration for a knowledge base path."""
    path: str
    session_only: bool = False


@dataclass
class Config:
    """Main configuration for lsearch."""
    name: str = "default"
    paths: List[PathConfig] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "node_modules/**",
        ".git/**",
        "__pycache__/**",
        "*.pyc",
        ".env",
        ".venv/**",
        "dist/**",
        "build/**",
    ])
    embedding_model: str = "bge-small-zh"
    token_limit: int = 4000
    auto_expand_links: bool = True
    chunk_size: int = 500
    chunk_overlap: int = 50

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load configuration from YAML file."""
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Convert path dictionaries to PathConfig objects
        paths = []
        for p in data.get("paths", []):
            if isinstance(p, dict):
                paths.append(PathConfig(**p))
            else:
                paths.append(PathConfig(path=p))

        # Get default exclude patterns from a temporary instance
        default_excludes = [
            "node_modules/**",
            ".git/**",
            "__pycache__/**",
            "*.pyc",
            ".env",
            ".venv/**",
            "dist/**",
            "build/**",
        ]

        return cls(
            name=data.get("name", "default"),
            paths=paths,
            exclude_patterns=data.get("exclude", default_excludes),
            embedding_model=data.get("embedding_model", "bge-small-zh"),
            token_limit=data.get("token_limit", 4000),
            auto_expand_links=data.get("auto_expand_links", True),
            chunk_size=data.get("chunk_size", 500),
            chunk_overlap=data.get("chunk_overlap", 50),
        )

    def to_file(self, path: Path) -> None:
        """Save configuration to YAML file."""
        data = {
            "name": self.name,
            "paths": [{"path": p.path, "session_only": p.session_only} for p in self.paths],
            "exclude": self.exclude_patterns,
            "embedding_model": self.embedding_model,
            "token_limit": self.token_limit,
            "auto_expand_links": self.auto_expand_links,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    @classmethod
    def get_global_dir(cls) -> Path:
        """Get the global lsearch directory."""
        home = Path.home()
        return home / ".lsearch"

    @classmethod
    def get_index_dir(cls, name: str) -> Path:
        """Get the index directory for a knowledge base."""
        return cls.get_global_dir() / "indices" / name

    def get_current_config_path(self) -> Optional[Path]:
        """Find the current project's config file."""
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            config_path = parent / ".lsearch" / "config.yaml"
            if config_path.exists():
                return config_path
        return None

    def get_effective_paths(self) -> List[PathConfig]:
        """Get all effective paths (project + session-only)."""
        paths = list(self.paths)

        # Add current directory if no paths configured
        if not paths:
            paths.append(PathConfig(path=".", session_only=False))

        return paths
