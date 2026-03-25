# lsearch - Claude Code Plugin

Local RAG knowledge base for Claude Code with hybrid semantic + keyword search.

## Installation

### Method 1: Auto-install (Recommended)

```bash
# Clone to Claude plugins directory
git clone https://github.com/moringchen/lsearch.git ~/.claude/plugins/lsearch

# Run install script
cd ~/.claude/plugins/lsearch && python install.py
```

### Method 2: Manual Install

1. **Clone the repository:**
   ```bash
   git clone https://github.com/moringchen/lsearch.git
   cd lsearch
   ```

2. **Install Python package:**
   ```bash
   pip install -e .
   ```

3. **Configure MCP Server** in `~/.claude/settings.json`:
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

4. **Copy skill and commands** (optional):
   ```bash
   cp -r .claude/skills/lsearch ~/.claude/skills/
   cp -r .claude/commands/* ~/.claude/commands/
   ```

## Quick Start

1. **Initialize knowledge base** in your project:
   ```bash
   lsearch init --name my-project --path ./docs
   ```

2. **Start using in Claude Code:**
   - `lsearch: How does authentication work?`
   - `@kb deployment process`
   - `/lsearch-index`

## Available Commands

| Command | Description |
|---------|-------------|
| `lsearch: <query>` | Search knowledge base (auto-trigger) |
| `@kb <query>` | Force knowledge base search |
| `/lsearch <query>` | Search via command |
| `/lsearch-index` | Index configured paths |
| `/lsearch-fetch <url>` | Fetch and index web page |
| `/lsearch-add <path>` | Add temporary session path |
| `/lsearch-stats` | Show knowledge base stats |

## Configuration

Create `.lsearch/config.yaml` in your project:

```yaml
name: my-project
paths:
  - ./docs
  - ./README.md
  - ./src
exclude:
  - node_modules/**
  - .git/**
embedding_model: all-MiniLM-L6-v2  # or bge-small-zh for Chinese
token_limit: 4000
auto_expand_links: true
```

## How It Works

```
Markdown Files → Chunks → Vector Index (Chroma) + BM25 Index + Link Graph
                                              ↓
                                    Hybrid Search (RRF Fusion)
                                              ↓
                                     Context Builder → Claude
```

## Features

- 🔍 **Hybrid Search**: Semantic (vector) + BM25 keyword + RRF fusion
- 🔗 **Link Graph**: Obsidian-style bidirectional links
- 🌐 **Web Fetching**: Index API docs, Swagger specs
- 🤖 **Local Models**: 70-300MB embedding models
- 💾 **Pure Local**: No cloud dependencies

## Requirements

- Python 3.10+
- Claude Code with MCP support

## License

MIT
