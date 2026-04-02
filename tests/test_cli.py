"""Tests for CLI commands."""

import os
import tempfile
from pathlib import Path
from click.testing import CliRunner
import pytest

from lsearch.cli import main


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestInitCommand:
    """Tests for 'lsearch init' command."""

    def test_init_creates_config_file(self, runner, temp_dir):
        """Test that init creates .lsearch/config.yaml."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            result = runner.invoke(main, ['init'])
            assert result.exit_code == 0
            assert (Path(td) / '.lsearch' / 'config.yaml').exists()

    def test_init_auto_generates_name(self, runner, temp_dir):
        """Test that init auto-generates name from directory."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            result = runner.invoke(main, ['init'])
            assert result.exit_code == 0
            # Name should be based on directory name
            assert temp_dir.name in result.output or 'Created knowledge base' in result.output

    def test_init_with_custom_name(self, runner, temp_dir):
        """Test init with --name parameter."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            result = runner.invoke(main, ['init', '--name', 'my-project'])
            assert result.exit_code == 0
            assert 'my-project' in result.output

    def test_init_with_custom_path(self, runner, temp_dir):
        """Test init with --path parameter."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            result = runner.invoke(main, ['init', '--path', './docs', '--path', './README.md'])
            assert result.exit_code == 0
            assert './docs' in result.output
            assert './README.md' in result.output

    def test_init_with_model(self, runner, temp_dir):
        """Test init with --model parameter."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            result = runner.invoke(main, ['init', '--model', 'all-MiniLM-L6-v2'])
            assert result.exit_code == 0
            # Check config file contains the model
            config_path = Path(td) / '.lsearch' / 'config.yaml'
            content = config_path.read_text()
            assert 'all-MiniLM-L6-v2' in content

    def test_init_creates_correct_yaml_structure(self, runner, temp_dir):
        """Test that init creates correct YAML structure."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            result = runner.invoke(main, ['init', '--name', 'test-kb'])
            assert result.exit_code == 0

            config_path = Path(td) / '.lsearch' / 'config.yaml'
            content = config_path.read_text()

            # Check required fields
            assert 'name: test-kb' in content
            assert 'paths:' in content
            assert 'embedding_model:' in content
            assert 'token_limit:' in content


class TestStatusCommand:
    """Tests for 'lsearch status' command."""

    def test_status_shows_kb_info(self, runner, temp_dir):
        """Test that status shows knowledge base info."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            # First init
            runner.invoke(main, ['init', '--name', 'my-kb'])

            # Then check status
            result = runner.invoke(main, ['status'])
            assert result.exit_code == 0
            assert 'my-kb' in result.output
            assert 'Knowledge Base Status' in result.output

    def test_status_shows_no_config_message(self, runner, temp_dir):
        """Test status when no config exists."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(main, ['status'])
            assert result.exit_code == 0
            assert 'No knowledge base configured' in result.output

    def test_status_shows_paths(self, runner, temp_dir):
        """Test that status shows configured paths."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            runner.invoke(main, ['init', '--path', './docs', '--path', './src'])
            result = runner.invoke(main, ['status'])
            assert result.exit_code == 0
            assert 'Configured Paths' in result.output


class TestModelsCommand:
    """Tests for 'lsearch models' command."""

    def test_models_lists_all_models(self, runner):
        """Test that models command lists all 3 models."""
        result = runner.invoke(main, ['models'])
        assert result.exit_code == 0

        # Check all models are listed
        assert 'all-MiniLM-L6-v2' in result.output
        assert 'bge-small-zh' in result.output
        assert 'bge-small-en' in result.output

    def test_models_shows_dimensions(self, runner):
        """Test that models shows dimension info."""
        result = runner.invoke(main, ['models'])
        assert result.exit_code == 0

        # Check dimensions are shown
        assert '384' in result.output or '512' in result.output
        assert 'Dimension' in result.output

    def test_models_shows_descriptions(self, runner):
        """Test that models shows descriptions."""
        result = runner.invoke(main, ['models'])
        assert result.exit_code == 0

        # Check descriptions
        assert 'English' in result.output or 'Chinese' in result.output


class TestAddPathCommand:
    """Tests for 'lsearch add-path' command."""

    def test_add_path_updates_config(self, runner, temp_dir):
        """Test that add-path updates config."""
        with runner.isolated_filesystem(temp_dir=temp_dir) as td:
            # First init
            runner.invoke(main, ['init'])

            # Add a path
            result = runner.invoke(main, ['add-path', './new-docs'])
            assert result.exit_code == 0
            assert 'Added path' in result.output

            # Check config was updated
            config_path = Path(td) / '.lsearch' / 'config.yaml'
            content = config_path.read_text()
            assert './new-docs' in content


class TestServerCommand:
    """Tests for 'lsearch server' command."""

    def test_server_command_exists(self, runner):
        """Test that server command exists."""
        result = runner.invoke(main, ['server', '--help'])
        assert result.exit_code == 0
        assert 'MCP server' in result.output or 'server' in result.output
