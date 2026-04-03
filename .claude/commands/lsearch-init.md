# /lsearch-init

Initialize lsearch knowledge base for the current project.

## Usage

```
/lsearch-init
```

This will launch an interactive setup to configure your knowledge base.

## What it does

1. **Knowledge Base Name** - Identifies your documentation collection
2. **Documentation Paths** - Select which directories/files to index
3. **Embedding Model** - Choose the embedding model for semantic search
4. **Create Configuration** - Saves to `.lsearch/config.yaml`

## After initialization

1. Create your documentation directory
2. Add markdown files
3. Run `/lsearch-index` to index documents
4. Start searching with `lsearch: <query>` or `/lsearch <query>`

## Example

```
/lsearch-init
# Then follow the interactive prompts to configure your knowledge base
```
