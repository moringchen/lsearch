# lsearch

[![PyPI version](https://badge.fury.io/py/lsearch.svg)](https://badge.fury.io/py/lsearch)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Local RAG (Retrieval-Augmented Generation) knowledge base for Claude Code. Search your project documentation using hybrid semantic + keyword search.

## Features

- 🔍 **Hybrid Search** - Combines semantic vector search (Chroma) with BM25 keyword search
- 🔗 **Link Graph** - Obsidian-style bidirectional link support with automatic expansion
- 🌐 **Web Fetching** - Download and index API documentation, Swagger specs
- 🤖 **Local Models** - Uses small embedding models (70-300MB), no cloud dependencies
- ⚡ **Fast** - Pure local operation with hot-loaded indices
- 📝 **Smart Context** - Token-aware context building with interactive selection

## Installation

```bash
pip install lsearch
```

Or install from source:

```bash
git clone https://github.com/moringchen/lsearch.git
cd lsearch
pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize Knowledge Base

```bash
# In your project directory
lsearch init --name my-project --path ./docs --path ./README.md
```

This creates `.lsearch/config.yaml`:

```yaml
name: my-project
paths:
  - path: ./docs
    session_only: false
  - path: ./README.md
    session_only: false
embedding_model: all-MiniLM-L6-v2
token_limit: 4000
auto_expand_links: true
```

### 2. Configure Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "lsearch": {
      "command": "python",
      "args": ["-m", "lsearch.server"]
    }
  }
}
```

### 3. Use in Claude Code

Once configured, use these triggers in Claude Code:

- `lsearch: How does authentication work?` - Automatic RAG search
- `@kb authentication flow` - Force knowledge base search

Or use commands:

- `/lsearch-index` - Index your documentation
- `/lsearch-fetch https://api.example.com/docs` - Fetch and index a web page
- `/lsearch-add /path/to/notes` - Add temporary path for this session

## How It Works

### Indexing

```
Markdown Files
      ↓
[Document Processor] → Chunks + Wiki-links
      ↓
┌─────────────┬─────────────┬─────────────┐
│   Chroma    │    BM25     │ Link Graph  │
│   (Vector)  │  (Keyword)  │  (NetworkX) │
└─────────────┴─────────────┴─────────────┘
      ↓
~/.lsearch/indices/{project-name}/
```

### Searching

1. **Vector Search** - Semantic similarity using embeddings
2. **BM25 Search** - Keyword matching with term frequency
3. **RRF Fusion** - Reciprocal Rank Fusion combines both
4. **Link Expansion** - Include linked notes
5. **Context Building** - Token-aware assembly

## Embedding Models

| Model | Size | Best For |
|-------|------|----------|
| `all-MiniLM-L6-v2` | 70MB | English general purpose |
| `bge-small-zh` | 300MB | Chinese optimized |
| `bge-small-en` | 130MB | English optimized |

Change in config:

```yaml
embedding_model: bge-small-zh
```

## Configuration Options

```yaml
name: my-project                          # Knowledge base name
paths:                                    # Paths to index
  - path: ./docs
    session_only: false
exclude:                                  # Patterns to exclude
  - node_modules/**
  - .git/**
  - "*.tmp"
embedding_model: all-MiniLM-L6-v2         # Embedding model
token_limit: 4000                         # Max tokens per query
auto_expand_links: true                   # Include linked notes
chunk_size: 500                           # Words per chunk
chunk_overlap: 50                         # Overlap between chunks
```

## CLI Commands

```bash
# Initialize a knowledge base
lsearch init --name my-project --path ./docs

# Add paths
lsearch add-path ./more-docs

# Check status
lsearch status

# List available models
lsearch models

# Run MCP server (for Claude Code)
lsearch server
```

## Web Fetching

Fetch and index web documentation:

```
/lsearch-fetch https://docs.python.org/3/library/asyncio.html
```

Supports:
- HTML documentation → Markdown
- Swagger/OpenAPI JSON → Markdown
- Auto title extraction

## Project Structure

```
lsearch/
├── src/lsearch/
│   ├── server.py              # MCP Server
│   ├── cli.py                 # CLI commands
│   ├── config.py              # Configuration
│   ├── embedding.py           # Embedding models
│   ├── document_processor.py  # Markdown processing
│   ├── fetcher.py             # URL fetching
│   ├── indexers/
│   │   ├── chroma_indexer.py  # Vector database
│   │   ├── bm25_indexer.py    # Keyword index
│   │   └── link_graph.py      # Note relationships
│   └── search/
│       ├── hybrid_search.py   # RRF fusion
│       └── context_builder.py # Token management
├── skill/SKILL.md             # Claude Code skill definition
└── tests/
```

## Development

```bash
# Setup
pip install -e ".[dev]"

# Format
black src/ tests/
ruff check src/ tests/

# Test
pytest
```

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please open an issue or PR.

## Acknowledgments

- [Chroma](https://www.trychroma.com/) - Vector database
- [Whoosh](https://whoosh.readthedocs.io/) - BM25 indexing
- [sentence-transformers](https://www.sbert.net/) - Embeddings
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
