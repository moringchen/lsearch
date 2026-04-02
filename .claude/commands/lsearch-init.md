---
name: lsearch-init
description: Initialize lsearch knowledge base with interactive guided setup (keyboard navigation). Must be run before using other lsearch commands.
---

Run the interactive initialization wizard in your terminal:

```bash
lsearch init
```

This will launch an interactive TUI where you can use ↑↓ arrow keys to navigate, Space to select, and Enter to confirm.

**What you'll configure:**
1. **Knowledge Base Name** - Auto-suggested from directory name
2. **Documentation Paths** - Select from common paths or enter custom
3. **Embedding Model** - Choose from 3 models (arrow keys + Enter)
4. **Confirmation** - Review and confirm your settings

**Alternative: Non-interactive mode**
If you prefer command-line arguments:
```bash
lsearch init --no-interactive --name my-project --path ./docs --model bge-small-zh
```

**After initialization:**
- Configuration saved to `.lsearch/config.yaml`
- Run `/lsearch-index` to index your documents
- Run `/lsearch <query>` to search
