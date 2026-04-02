# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

lsearch is a Local RAG (Retrieval-Augmented Generation) knowledge base plugin for Claude Code. It provides hybrid semantic + keyword search over markdown documentation using three parallel indexers: ChromaDB (vector), Whoosh/BM25 (keyword), and NetworkX (link graph).

## Development Commands

### Setup
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lsearch --cov-report=xml

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::test_config_save_load
```

### Linting and Formatting
```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check
mypy src/
```

### Running the Server
```bash
# Run MCP server (for Claude Code integration)
lsearch server

# Or via module
python -m lsearch.server
```

### CLI Commands
```bash
# Initialize knowledge base in current directory
lsearch init

# Check status
lsearch status

# List available embedding models
lsearch models
```

## Architecture

### Data Flow

```
Markdown Files → DocumentProcessor → Chunks
                                          ↓
                    ┌───────────────────────┼───────────────────────┐
                    ↓                       ↓                       ↓
              ChromaIndexer            BM25Indexer            LinkGraph
              (vector/search)          (keyword/search)       (note relationships)
                    └───────────────────────┬───────────────────────┘
                                            ↓
                              HybridSearcher (RRF Fusion)
                                            ↓
                              ContextBuilder (token management)
                                            ↓
                                        MCP Server
```

### Core Components

**Entry Points:**
- `src/lsearch/server.py` - MCP server (main entry for Claude Code)
- `src/lsearch/cli.py` - CLI commands (`lsearch init`, `lsearch status`, etc.)
- `src/lsearch/__main__.py` - Module entry point

**Indexing Pipeline:**
- `DocumentProcessor` - Parses markdown, extracts frontmatter/YAML, wiki-links (`[[Note]]`), splits into overlapping chunks
- `ChromaIndexer` - Vector embeddings using sentence-transformers, cosine similarity search
- `BM25Indexer` - Keyword search using Whoosh with stemming analyzer
- `LinkGraph` - NetworkX graph for Obsidian-style bidirectional link navigation

**Search Pipeline:**
- `HybridSearcher` - Combines vector + BM25 results using Reciprocal Rank Fusion (RRF with k=60 constant)
- `ContextBuilder` - Assembles results respecting token limits (default 4000)

**Configuration:**
- `Config` - Loads from `.lsearch/config.yaml`, stores indices in `~/.lsearch/indices/<name>/`

### Key Design Patterns

1. **RRF Fusion**: Combines rankings from vector and keyword search using `score = 1/(k + rank)` where k=60
2. **Dual Storage**: Each document chunk is stored in both ChromaDB and Whoosh indices
3. **Session Paths**: Temporary paths can be added per-session (not persisted to config)
4. **Lazy Loading**: Config and indices are initialized on first tool call, not at import
5. **Global + Project Config**: Indices stored in `~/.lsearch/`, config in project `.lsearch/config.yaml`

### File Organization

```
src/lsearch/
├── server.py              # MCP server with stdio transport
├── cli.py                 # Click-based CLI
├── config.py              # Config dataclass with YAML serialization
├── document_processor.py  # Markdown parsing, chunking, frontmatter extraction
├── embedding.py           # Embedding model management (sentence-transformers)
├── fetcher.py             # URL fetching (HTML→Markdown, Swagger JSON)
├── indexers/
│   ├── chroma_indexer.py  # Vector index with ChromaDB
│   ├── bm25_indexer.py    # Keyword index with Whoosh
│   └── link_graph.py      # NetworkX graph for wiki-links
└── search/
    ├── hybrid_search.py   # RRF fusion searcher
    └── context_builder.py # Token-aware context assembly
```

### Testing Structure

Tests use `pytest` with fixtures in `tests/`:
- `test_config.py` - Config serialization/deserialization
- `test_document_processor.py` - Markdown parsing and chunking
- `test_cli.py` - CLI command testing

Tests use `tempfile.TemporaryDirectory` for isolation.

### MCP Integration

The server exposes 7 tools to Claude Code via MCP:
- `search` - Basic hybrid search
- `search_with_context` - Search with formatted LLM-ready context
- `index` - Trigger indexing of configured paths
- `fetch_url` - Download and index web pages
- `add_path` - Add temporary session path
- `list_paths` - Show configured paths
- `get_stats` - Show index statistics

Slash commands in `.claude/commands/` provide shortcuts:
- `/lsearch <query>` → `search_with_context`
- `/lsearch-index` → `index`
- `/lsearch-fetch <url>` → `fetch_url`
- `/lsearch-add <path>` → `add_path`
- `/lsearch-stats` → `get_stats`

### Embedding Models

Three models supported (defined in `embedding.py`):
- `bge-small-zh` (300MB, Chinese-optimized, default)
- `all-MiniLM-L6-v2` (70MB, English general purpose)
- `bge-small-en` (130MB, English-optimized)

Models download automatically on first use via sentence-transformers.

### Installation

The `install.py` script:
1. Installs package with `pip install -e .`
2. Configures MCP server in `~/.claude/settings.json`
3. Copies skill definition to `~/.claude/skills/`
4. Copies slash commands to `~/.claude/commands/`

Claude Code must be restarted after installation for slash commands to appear.
