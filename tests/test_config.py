"""Tests for config module."""

import tempfile
from pathlib import Path

import pytest

from lsearch.config import Config, PathConfig


def test_default_config():
    """Test default configuration values."""
    config = Config()
    assert config.name == "default"
    assert config.embedding_model == "bge-small-zh"
    assert config.token_limit == 4000
    assert config.auto_expand_links is True


def test_path_config():
    """Test PathConfig dataclass."""
    pc = PathConfig(path="./docs", session_only=True)
    assert pc.path == "./docs"
    assert pc.session_only is True


def test_config_save_load():
    """Test saving and loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"

        config = Config(
            name="test-project",
            paths=[PathConfig(path="./docs", session_only=False)],
            embedding_model="bge-small-zh",
            token_limit=2000,
        )

        config.to_file(config_path)
        assert config_path.exists()

        loaded = Config.from_file(config_path)
        assert loaded.name == "test-project"
        assert loaded.embedding_model == "bge-small-zh"
        assert loaded.token_limit == 2000
        assert len(loaded.paths) == 1
        assert loaded.paths[0].path == "./docs"


def test_get_global_dir():
    """Test global directory path."""
    global_dir = Config.get_global_dir()
    assert global_dir.name == ".lsearch"
    assert global_dir.parent == Path.home()


def test_get_index_dir():
    """Test index directory path."""
    index_dir = Config.get_index_dir("my-project")
    assert "my-project" in str(index_dir)
    assert "indices" in str(index_dir)
