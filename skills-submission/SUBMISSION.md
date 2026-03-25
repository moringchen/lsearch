# Skills.sh Submission Template for lsearch

## Submission Information

**Skill Name:** lsearch

**Repository:** https://github.com/moringchen/lsearch

**Marketplace JSON Path:** `.claude-plugin/marketplace.json`

---

## Skill Description

**Short Description (50 chars max):**
Local RAG knowledge base for Claude Code

**Full Description:**
lsearch is a local RAG (Retrieval-Augmented Generation) knowledge base plugin for Claude Code. It enables hybrid semantic + BM25 keyword search over project documentation, with support for:

- 🔍 **Hybrid Search**: Combines semantic vector search (Chroma) with BM25 keyword search using RRF fusion
- 🔗 **Link Graph**: Obsidian-style bidirectional links with automatic expansion
- 🌐 **Web Fetching**: Download and index API documentation, Swagger specs
- 🤖 **Local Models**: Uses small embedding models (70-300MB), no cloud dependencies
- 💾 **Pure Local**: All data stays on your machine
- 🎯 **Keyword Auto-Trigger**: Smart detection with "knowledge base"/"auto search" keywords

**Category:** Productivity / Knowledge Management

**Tags:** rag, search, knowledge-base, mcp, semantic-search, documentation, chinese

---

## Installation Methods

Users can install via:

```bash
# Method 1: Direct from GitHub (recommended)
npx skills add moringchen/lsearch -g

# Method 2: From PyPI
pip install lsearch
```

---

## Technical Details

**Runtime:** Python 3.10+

**MCP Transport:** stdio

**MCP Server Command:**
```json
{
  "command": "python",
  "args": ["-m", "lsearch.server"]
}
```

**Available Tools:**
- `mcp__lsearch__search` - Search knowledge base
- `mcp__lsearch__search_with_context` - Search with full context building
- `mcp__lsearch__index` - Index documents
- `mcp__lsearch__fetch_url` - Fetch and index web pages
- `mcp__lsearch__add_path` - Add temporary paths
- `mcp__lsearch__list_paths` - List configured paths
- `mcp__lsearch__get_stats` - Get knowledge base statistics

---

## Author Information

**Name:** moringchen

**Email:** 843115404@qq.com

**GitHub:** https://github.com/moringchen

---

## License

MIT License

---

## Additional Notes for Reviewers

1. **Chinese Optimized**: Default embedding model is `bge-small-zh` (300MB), optimized for Chinese text
2. **Zero Cloud Dependencies**: All models run locally, no API keys needed
3. **Hot-loaded Indices**: Fast startup with pre-built indices
4. **Cross-platform**: Works on macOS, Linux, and Windows

---

## Submission Checklist

- [x] Repository is public
- [x] Marketplace JSON is valid
- [x] Includes README with installation instructions
- [x] Includes LICENSE file (MIT)
- [x] MCP server tested and working
- [x] Skill follows naming conventions (lowercase, no special chars)

---

## How to Get Listed on skills.sh

> 📌 **Good News:** According to the [skills.sh FAQ](https://skills.sh/faq), skills appear on the leaderboard **automatically** through anonymous telemetry when users install them!

### How It Works

The skills leaderboard is powered by anonymous telemetry from the skills CLI. When users run:

```bash
npx skills add moringchen/lsearch -g
```

Your skill will be tracked and appear on skills.sh based on installation count. **No manual submission required!**

### What You Need to Do

1. **Make sure your repository is public** ✅ (Already done)
2. **Ensure marketplace.json is valid** ✅ (Already done)
3. **Share your skill with users** - The more people install it, the higher it ranks

### Sharing Your Skill

Share this installation command with your users:

```bash
npx skills add moringchen/lsearch -g
```

Or share the PyPI package:

```bash
pip install lsearch
```

### Tracking Your Progress

Once users start installing your skill:
- It will appear on https://skills.sh leaderboard
- Ranking is based on installation count
- No personal data is collected - only aggregate counts

### Self-Hosted Marketplace (Optional)

For team/private distribution, use the `example-marketplace/` in this repo.

---

**Status:** 🚀 Ready - Just need users to install!
