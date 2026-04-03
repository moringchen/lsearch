# /lsearch-init

Initialize or reconfigure lsearch knowledge base for the current project.

## Usage

```
/lsearch-init
```

This will launch an interactive form to configure your knowledge base.

## What it does

If not initialized:
1. **Knowledge Base Name** - Identifies your documentation collection
2. **Documentation Paths** - Select directories/files to index (checkboxes)
3. **Embedding Model** - Choose the embedding model (dropdown)
4. **Custom Paths** - Add additional paths (optional)
5. **Create Configuration** - Saves to `.lsearch/config.yaml`

If already initialized:
1. **Show Current Config** - Displays existing name, paths, and model
2. **Choose Action** - Keep current or modify via form
3. **Force Reinitialize** - Check this to overwrite existing configuration

## After initialization

1. Create your documentation directory
2. Add markdown files
3. Run `/lsearch-index` to index documents
4. Start searching with `lsearch: <query>` or `/lsearch <query>`

## Example

```
/lsearch-init
# Follow the interactive form to configure or update your knowledge base
```
