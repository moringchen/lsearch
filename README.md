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

# Run install script (IMPORTANT: Required for slash commands to work)
cd ~/.claude/plugins/lsearch && python install.py
```

**⚠️ You must restart Claude Code after installation for slash commands (`/lsearch`, `/lsearch-index`, etc.) to appear.**

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

### Option 3: Skills CLI (npx skills)

Install via the Skills CLI from [skills.sh](https://skills.sh):

```bash
# Install lsearch skill
npx skills add moringchen/lsearch -g

# Or install from PyPI via skills
npx skills add moringchen/lsearch@pip -g
```

The `-g` flag installs globally (user-level).

### Option 4: Development Install

```bash
git clone https://github.com/moringchen/lsearch.git
cd lsearch
pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize Knowledge Base

```bash
# In your project directory
# Auto-generates name from directory, uses ./docs as default path
lsearch init

# Or customize name and paths
lsearch init --name my-project --path ./docs --path ./README.md
```

**Auto-generated names:**
- If run in `/home/user/projects/my-app`, name becomes: `my-app`
- If `my-app` already exists, name becomes: `projects-my-app`

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

### Keyword-Based Auto-Trigger

When the user asks questions containing specific keywords, automatically search the knowledge base:

**Trigger Keywords:**
- "knowledge base" / "知识库"
- "auto search" / "自动搜索"

**Examples of auto-trigger:**
- "Search knowledge base for auth" → Auto-search
- "自动搜索部署文档" → Auto-search
- "Use knowledge base" → Auto-search
- "请自动搜索相关文档" → Auto-search

**How it works:**
1. Detect keywords in user query
2. Automatically call `mcp__lsearch__search_with_context`
3. Include results in response

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
embedding_model: bge-small-zh             # Embedding model (default: Chinese-optimized)
token_limit: 4000                         # Max tokens per query
auto_expand_links: true                   # Include linked notes
chunk_size: 500                           # Words per chunk
chunk_overlap: 50                         # Overlap between chunks
```

### Embedding Models

| Model | Size | Best For | Language | Default |
|-------|------|----------|----------|---------|
| `bge-small-zh` | 300MB | Optimized for Chinese | Chinese | ✅ Default |
| `all-MiniLM-L6-v2` | 70MB | General purpose | English | |
| `bge-small-en` | 130MB | Optimized for English | English | |

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

## Usage Examples

### Example 1: Project Documentation Setup

```bash
# Navigate to your project
cd ~/projects/my-web-app

# Initialize with default settings (auto-generated name, ./docs path)
lsearch init

# Create docs directory and add files
mkdir -p docs
echo "# API Documentation" > docs/api.md
echo "# Deployment Guide" > docs/deployment.md

# In Claude Code, index the documents
/lsearch-index

# Search your documentation
lsearch: How do I deploy this project?
```

### Example 2: Multi-language Project

```bash
# Initialize with Chinese-optimized model (default)
lsearch init --name backend-api

# Add multiple documentation paths
lsearch init --name fullstack \
  --path ./backend/docs \
  --path ./frontend/docs \
  --path ./README.md \
  --model bge-small-zh
```

### Example 3: Web Documentation

```bash
# Fetch and index external API docs
/lsearch-fetch https://docs.example.com/api

# Search the fetched documentation
@kb example API authentication
```

### Example 4: Temporary Knowledge Base

```bash
# Add a temporary path for this session only
/lsearch-add ~/personal-notes/project-ideas.md

# Search includes both project docs and temporary notes
lsearch: What are the project requirements?
```

### Example 5: Multi-Project Knowledge

```yaml
# .lsearch/config.yaml
name: work-projects
paths:
  - path: ~/work/project-a/docs
    session_only: false
  - path: ~/work/project-b/docs
    session_only: false
  - path: ~/work/shared-guides
    session_only: false
exclude:
  - "**/node_modules/**"
  - "**/.git/**"
embedding_model: bge-small-zh
token_limit: 4000
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
