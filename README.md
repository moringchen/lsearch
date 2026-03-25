# lsearch

[![PyPI version](https://badge.fury.io/py/lsearch.svg)](https://badge.fury.io/py/lsearch)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**English** | [中文](README.zh.md)

Local RAG (Retrieval-Augmented Generation) knowledge base for Claude Code. Search your project documentation using hybrid semantic + keyword search.

## Features

- 🔍 **Hybrid Search** - Combines semantic vector search (Chroma) with BM25 keyword search
- 🔗 **Link Graph** - Obsidian-style bidirectional link support with automatic expansion
- 🌐 **Web Fetching** - Download and index API documentation, Swagger specs
- 🤖 **Local Models** - Uses small embedding models (70-300MB), no cloud dependencies
- ⚡ **Fast** - Pure local operation with hot-loaded indices
- 📝 **Smart Context** - Token-aware context building with interactive selection
- 🎯 **Multiple Triggers** - Use `lsearch:`, `@kb`, or slash commands

## Installation

### Option 1: Claude Code Plugin (Recommended)

Install as a Claude Code plugin with automatic MCP configuration:

```bash
# Clone to Claude plugins directory
git clone https://github.com/moringchen/lsearch.git ~/.claude/plugins/lsearch

# Run install script
cd ~/.claude/plugins/lsearch && python install.py
```

Then restart Claude Code.

### Option 2: PyPI

```bash
pip install lsearch
```

Then manually add to `~/.claude/settings.json`:

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

### Option 3: Development Install

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

### 2. Use in Claude Code

Once configured, use these triggers in Claude Code:

| Trigger | Description | Example |
|---------|-------------|---------|
| `lsearch: <query>` | Automatic RAG search | `lsearch: How does auth work?` |
| `@kb <query>` | Force knowledge base search | `@kb deployment process` |
| `/lsearch <query>` | Search via slash command | `/lsearch API documentation` |
| `/lsearch-index` | Manually trigger indexing | `/lsearch-index` |
| `/lsearch-fetch <url>` | Fetch and index web page | `/lsearch-fetch https://docs.example.com` |
| `/lsearch-add <path>` | Add temporary path for session | `/lsearch-add ~/notes` |
| `/lsearch-stats` | Show knowledge base statistics | `/lsearch-stats` |

## How It Works

```
Markdown Files → Chunks → Vector Index (Chroma) + BM25 Index + Link Graph
                                              ↓
                                    Hybrid Search (RRF Fusion)
                                              ↓
                                     Context Builder → Claude
```

### Indexing Process

1. **Document Processing** - Markdown files are parsed, frontmatter extracted, wiki-links identified
2. **Chunking** - Documents split into overlapping chunks (default 500 words)
3. **Embedding** - Each chunk embedded using local models (all-MiniLM-L6-v2 or bge-small-zh)
4. **Indexing** - Stored in Chroma (vector) + Whoosh (BM25) + NetworkX (link graph)

### Search Process

1. **Vector Search** - Semantic similarity using cosine distance
2. **BM25 Search** - Keyword matching with term frequency
3. **RRF Fusion** - Reciprocal Rank Fusion combines both results
4. **Link Expansion** - Include linked notes if enabled
5. **Context Building** - Assemble results respecting token limits

## Configuration

### Config File (`.lsearch/config.yaml`)

```yaml
name: my-project                          # Knowledge base name
paths:                                    # Paths to index
  - path: ./docs
    session_only: false
  - path: ./README.md
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

### Embedding Models

| Model | Size | Best For | Language |
|-------|------|----------|----------|
| `all-MiniLM-L6-v2` | 70MB | General purpose | English |
| `bge-small-zh` | 300MB | Optimized for Chinese | Chinese |
| `bge-small-en` | 130MB | Optimized for English | English |

## CLI Commands

```bash
# Initialize a knowledge base
lsearch init --name my-project --path ./docs

# Add paths to existing knowledge base
lsearch add-path ./more-docs

# Check status and statistics
lsearch status

# List available embedding models
lsearch models

# Run MCP server (for Claude Code integration)
lsearch server
```

## Web Fetching

Fetch and index web documentation:

```
/lsearch-fetch https://docs.python.org/3/library/asyncio.html
```

Supports:
- **HTML** → Markdown conversion
- **Swagger/OpenAPI JSON** → Markdown
- **Auto title extraction**

Fetched documents are stored in `~/.lsearch/fetched/` and indexed.

## Project Structure

```
lsearch/
├── src/lsearch/
│   ├── server.py              # MCP Server (main entry)
│   ├── cli.py                 # CLI commands
│   ├── config.py              # Configuration management
│   ├── embedding.py           # Embedding models
│   ├── document_processor.py  # Markdown processing
│   ├── fetcher.py             # URL fetching
│   ├── indexers/
│   │   ├── chroma_indexer.py  # Vector database (Chroma)
│   │   ├── bm25_indexer.py    # Keyword index (Whoosh)
│   │   └── link_graph.py      # Note relationships (NetworkX)
│   └── search/
│       ├── hybrid_search.py   # RRF fusion
│       └── context_builder.py # Token management
├── .claude/
│   ├── commands/              # Slash commands
│   └── skills/                # Skill definition
├── skill/
│   └── SKILL.md               # Claude Code skill definition
├── install.py                 # Installation script
├── README.md                  # This file
├── README.zh.md               # Chinese documentation
└── pyproject.toml             # Package configuration
```

## Development

```bash
# Setup
pip install -e ".[dev]"

# Format code
black src/ tests/
ruff check src/ tests/

# Run tests
pytest

# Type checking
mypy src/
```

## Troubleshooting

### Issue: MCP server not starting

**Solution**: Check if lsearch is installed:
```bash
python -m lsearch.server --version
```

If not installed, run:
```bash
pip install lsearch
```

### Issue: No search results

**Solution**: Ensure documents are indexed:
```bash
/lsearch-index
```

Or check index status:
```bash
/lsearch-stats
```

### Issue: Model download fails

**Solution**: Embedding models are downloaded on first use. Ensure you have:
- Internet connection (first time only)
- ~300MB disk space for Chinese model, ~70MB for English

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please open an issue or PR.

## Acknowledgments

- [Chroma](https://www.trychroma.com/) - Vector database
- [Whoosh](https://whoosh.readthedocs.io/) - BM25 indexing
- [sentence-transformers](https://www.sbert.net/) - Embeddings
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol

## Contact

- GitHub: [@moringchen](https://github.com/moringchen)
- Email: 843115404@qq.com
