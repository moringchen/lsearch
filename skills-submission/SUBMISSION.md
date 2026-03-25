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

## How to Submit

> ⚠️ **Note:** skills.sh currently does not have a public submission form. Here are alternative approaches:

### Option 1: Direct Installation (Recommended for Now)
Users can install lsearch directly without it being indexed:

```bash
npx skills add moringchen/lsearch -g
```

### Option 2: Contact Skills.sh Team
Try reaching out through:
- Claude Code Discord community
- Anthropic support channels
- GitHub Discussions in related repositories

### Option 3: Create Issue in Community Registry
Some community members maintain unofficial registries. Search for:
- `skills-registry` on GitHub
- `claude-code-skills` topics

### Option 4: Self-Hosted Marketplace
Use the `example-marketplace/` in this repo to create your own marketplace for your team.

---

**Submission Date:** _YYYY-MM-DD_

**Submitter:** _Your Name/Handle_

**Status:** ⏳ Waiting for skills.sh to open public submissions
