"""MCP Server for lsearch."""

import json
import os
from pathlib import Path
from typing import AsyncIterator

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from lsearch.config import Config, PathConfig
from lsearch.document_processor import DocumentProcessor
from lsearch.fetcher import URLFetcher
from lsearch.search import HybridSearcher, ContextBuilder

# Global state
_config: Config | None = None
_searcher: HybridSearcher | None = None
_processor: DocumentProcessor | None = None
_builder: ContextBuilder | None = None
_session_paths: list[PathConfig] = []

server = Server("lsearch")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search",
            description="Search the knowledge base using hybrid semantic + keyword search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10,
                    },
                    "expand_links": {
                        "type": "boolean",
                        "description": "Include linked notes in results",
                        "default": True,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="search_with_context",
            description="Search and return formatted context ready for LLM consumption",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens in context",
                        "default": 4000,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="index",
            description="Manually trigger indexing of knowledge base paths",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Specific path to index (optional, defaults to all configured paths)",
                    },
                },
            },
        ),
        Tool(
            name="fetch_url",
            description="Fetch a URL and add to knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch",
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional title for the document",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="add_path",
            description="Add a temporary path to the current session's knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to add",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="list_paths",
            description="List all configured knowledge base paths",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_stats",
            description="Get knowledge base statistics",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    global _config, _searcher, _processor, _builder, _session_paths

    # Initialize on first call
    if _config is None:
        _init_config()

    if name == "search":
        return await _handle_search(arguments)
    elif name == "search_with_context":
        return await _handle_search_with_context(arguments)
    elif name == "index":
        return await _handle_index(arguments)
    elif name == "fetch_url":
        return await _handle_fetch_url(arguments)
    elif name == "add_path":
        return await _handle_add_path(arguments)
    elif name == "list_paths":
        return await _handle_list_paths()
    elif name == "get_stats":
        return await _handle_get_stats()
    else:
        raise ValueError(f"Unknown tool: {name}")


def _init_config() -> None:
    """Initialize configuration and components."""
    global _config, _searcher, _processor, _builder

    # Try to load project config
    temp_config = Config()
    config_path = temp_config.get_current_config_path()

    if config_path:
        _config = Config.from_file(config_path)
    else:
        _config = Config()

    _searcher = HybridSearcher(_config)
    _processor = DocumentProcessor(_config)
    _builder = ContextBuilder(_config)


async def _handle_search(arguments: dict) -> list[TextContent]:
    """Handle search tool."""
    query = arguments["query"]
    limit = arguments.get("limit", 10)
    expand_links = arguments.get("expand_links", True)

    results = _searcher.search(query, top_k=limit, expand_links=expand_links)

    # Format results
    formatted = []
    for i, result in enumerate(results, 1):
        meta = result["metadata"]
        text = result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"]
        formatted.append(
            f"{i}. **{meta.get('title', 'Untitled')}** (score: {result['score']:.3f})\n"
            f"   File: `{meta['file_path']}`\n"
            f"   {text}\n"
        )

    content = f"Found {len(results)} results for '{query}':\n\n"
    content += "\n".join(formatted)

    return [TextContent(type="text", text=content)]


async def _handle_search_with_context(arguments: dict) -> list[TextContent]:
    """Handle search_with_context tool."""
    query = arguments["query"]
    max_tokens = arguments.get("max_tokens", _config.token_limit if _config else 4000)

    # Search
    results = _searcher.search(query, top_k=15, expand_links=True)

    # Build context
    context = _builder.build_context(results, max_tokens=max_tokens)

    # Add summary
    summary = f"""
# Search Summary
- Query: {query}
- Total results: {context['total_results']}
- Used in context: {len(context['used_results'])}
- Excluded (token limit): {len(context['excluded_results'])}
- Context tokens: {context['total_tokens']}

---

{context['content']}
"""

    return [TextContent(type="text", text=summary)]


async def _handle_index(arguments: dict) -> list[TextContent]:
    """Handle index tool."""
    specific_path = arguments.get("path")

    paths_to_index = []
    if specific_path:
        paths_to_index = [PathConfig(path=specific_path)]
    else:
        paths_to_index = _config.get_effective_paths() + _session_paths

    indexed_count = 0
    errors = []

    for path_config in paths_to_index:
        path = Path(path_config.path).expanduser().resolve()

        if not path.exists():
            errors.append(f"Path does not exist: {path}")
            continue

        if path.is_file():
            # Index single file
            try:
                _index_single_file(str(path))
                indexed_count += 1
            except Exception as e:
                errors.append(f"Error indexing {path}: {e}")
        else:
            # Index directory
            for file_path in path.rglob("*.md"):
                if _processor.should_index(str(file_path)):
                    try:
                        _index_single_file(str(file_path))
                        indexed_count += 1
                    except Exception as e:
                        errors.append(f"Error indexing {file_path}: {e}")

    result = f"Indexed {indexed_count} files."
    if errors:
        result += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors[:5])

    return [TextContent(type="text", text=result)]


def _index_single_file(file_path: str) -> None:
    """Index a single file."""
    chunks, metadata = _processor.process_file(file_path)
    _searcher.index_file(
        file_path=file_path,
        chunks=chunks,
        title=metadata.get("title", ""),
        links=metadata.get("links", []),
    )


async def _handle_fetch_url(arguments: dict) -> list[TextContent]:
    """Handle fetch_url tool."""
    url = arguments["url"]
    title = arguments.get("title")

    fetcher = URLFetcher()

    try:
        content = fetcher.fetch(url)
        fetched_title = title

        if not fetched_title:
            # Extract title from content
            lines = content.split("\n")
            for line in lines:
                if line.startswith("# "):
                    fetched_title = line[2:].strip()
                    break

        # Generate filename
        filename = fetcher.get_filename_from_url(url, fetched_title)

        # Save to global fetch directory
        fetch_dir = Config.get_global_dir() / "fetched"
        fetch_dir.mkdir(parents=True, exist_ok=True)

        file_path = fetch_dir / filename

        # Add source URL to content
        full_content = f"---\ntitle: {fetched_title or filename}\nsource_url: {url}\nfetched: true\n---\n\n{content}"

        file_path.write_text(full_content, encoding="utf-8")

        # Index the file
        chunks, metadata = _processor.process_content(full_content, str(file_path))
        _searcher.index_file(
            file_path=str(file_path),
            chunks=chunks,
            title=metadata.get("title", fetched_title or filename),
            links=metadata.get("links", []),
        )

        return [TextContent(
            type="text",
            text=f"Fetched and indexed: {url}\nSaved as: {file_path}\nTitle: {fetched_title or filename}"
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error fetching {url}: {e}")]


async def _handle_add_path(arguments: dict) -> list[TextContent]:
    """Handle add_path tool."""
    path = arguments["path"]
    expanded_path = Path(path).expanduser().resolve()

    if not expanded_path.exists():
        return [TextContent(type="text", text=f"Path does not exist: {path}")]

    # Add to session paths
    path_config = PathConfig(path=str(expanded_path), session_only=True)
    _session_paths.append(path_config)

    return [TextContent(type="text", text=f"Added to session paths: {expanded_path}")]


async def _handle_list_paths() -> list[TextContent]:
    """Handle list_paths tool."""
    lines = ["Configured paths:"]

    for i, path_config in enumerate(_config.get_effective_paths(), 1):
        session_tag = " [session]" if path_config.session_only else ""
        lines.append(f"{i}. {path_config.path}{session_tag}")

    if _session_paths:
        lines.append("\nSession-only paths:")
        for i, path_config in enumerate(_session_paths, 1):
            lines.append(f"{i}. {path_config.path}")

    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_get_stats() -> list[TextContent]:
    """Handle get_stats tool."""
    stats = _searcher.get_stats()

    lines = [
        "Knowledge Base Statistics:",
        "",
        f"Vector Index (Chroma):",
        f"  Documents: {stats['chroma']['count']}",
        f"  Location: {stats['chroma']['index_dir']}",
        "",
        f"Keyword Index (BM25):",
        f"  Documents: {stats['bm25']['count']}",
        f"  Location: {stats['bm25']['index_dir']}",
        "",
        f"Link Graph:",
        f"  Notes: {stats['link_graph']['nodes']}",
        f"  Links: {stats['link_graph']['edges']}",
    ]

    return [TextContent(type="text", text="\n".join(lines))]


def main() -> None:
    """Run the MCP server."""
    import asyncio

    async def run():
        async with stdio_server(server) as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
