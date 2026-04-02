---
name: lsearch-init
description: Initialize lsearch knowledge base with interactive TUI (keyboard navigation). Run in your local terminal.
---

I'll help you initialize lsearch for this project. Please run the following command in your **local terminal** (not in Claude Code):

```bash
lsearch init
```

This will launch an interactive TUI where you can use keyboard navigation:

| Key | Action |
|-----|--------|
| ↑ ↓ | Navigate up/down |
| Space | Select/deselect (checkbox) |
| Enter | Confirm selection |
| Ctrl+C | Cancel |

## What you'll configure

**Step 1: Knowledge Base Name**
- Auto-suggested based on directory name
- Edit or accept with Enter

**Step 2: Documentation Paths**  
- Select from common paths:
  - `./docs` - Documentation folder
  - `./README.md` - Main readme
  - `./src` - Source code
  - `./notes` - Notes folder
- Use Space to toggle selection

**Step 3: Embedding Model**
- 🌏 `bge-small-zh` - Chinese optimized (~300MB)
- 🇬🇧 `all-MiniLM-L6-v2` - English, small & fast (~70MB)  
- 🇬🇧 `bge-small-en` - English optimized (~130MB)

**Step 4: Confirm & Create**
- Review your settings
- Confirm to create `.lsearch/config.yaml`

---

## Alternative: Quick init with defaults

If you want to use defaults without TUI:

```bash
lsearch init --no-interactive --name <name> --path <paths> --model <model>
```

Example:
```bash
lsearch init --no-interactive --name my-docs --path ./docs --model bge-small-zh
```

---

## After initialization

Once configured, you can use these commands in Claude Code:
- `/lsearch-index` - Index your documents
- `/lsearch <query>` - Search knowledge base
- `/lsearch-stats` - View statistics

Please run `lsearch init` in your terminal and let me know when you're done!
