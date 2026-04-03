"""CLI for lsearch."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from lsearch.config import Config, PathConfig
from lsearch.server import main as server_main

console = Console()


@click.group()
@click.version_option(version="0.2.0")
def main():
    """lsearch - Local RAG knowledge base for Claude Code."""
    pass


@main.command()
def server():
    """Run the MCP server (for Claude Code integration)."""
    server_main()


@main.command()
@click.option(
    "--name",
    default=None,
    help="Knowledge base name (default: auto-generated from directory)",
)
@click.option(
    "--path",
    multiple=True,
    help="Paths to include in the knowledge base (default: ./docs)",
)
@click.option(
    "--model",
    default="bge-small-zh",
    type=click.Choice(["bge-small-zh", "all-MiniLM-L6-v2", "bge-small-en"]),
    help="Embedding model to use",
)
def init(name: str | None, path: tuple, model: str):
    """Initialize a new knowledge base configuration."""
    # Generate default name if not provided
    if name is None:
        cwd = Path.cwd()
        name = cwd.name
        parent = cwd.parent
        if parent.name and parent != cwd:
            name = f"{parent.name}-{name}"

    paths = list(path) if path else ["./docs"]

    config = Config(
        name=name,
        paths=[PathConfig(path=p, session_only=False) for p in paths],
        embedding_model=model,
    )

    config_dir = Path(".lsearch")
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.yaml"

    config.to_file(config_file)

    console.print(f"[green]Created knowledge base: {name}[/green]")
    console.print(f"Configuration saved to: {config_file}")
    console.print(f"\nPaths configured: {', '.join(paths)}")
    console.print("\nNext steps:")
    console.print("  1. Create your docs directory: mkdir -p ./docs")
    console.print("  2. Add markdown files to ./docs")
    console.print("  3. In Claude Code, run: /lsearch-index")


@main.command()
@click.argument("path")
def add_path(path: str):
    """Add a path to the current knowledge base."""
    config_path = Path(".lsearch/config.yaml")

    if config_path.exists():
        config = Config.from_file(config_path)
    else:
        config = Config()

    config.paths.append(PathConfig(path=path, session_only=False))
    config.to_file(config_path)

    console.print(f"[green]Added path: {path}[/green]")


@main.command()
def status():
    """Show knowledge base status."""
    config_path = Path(".lsearch/config.yaml")

    if not config_path.exists():
        console.print("[yellow]No knowledge base configured.[/yellow]")
        console.print("Run in Claude Code: /lsearch-init")
        return

    config = Config.from_file(config_path)

    table = Table(title="Knowledge Base Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Name", config.name)
    table.add_row("Embedding Model", config.embedding_model)
    table.add_row("Token Limit", str(config.token_limit))
    table.add_row("Auto Expand Links", str(config.auto_expand_links))

    console.print(table)

    console.print("\n[bold]Configured Paths:[/bold]")
    for i, p in enumerate(config.paths, 1):
        session_tag = " [session]" if p.session_only else ""
        console.print(f"  {i}. {p.path}{session_tag}")


@main.command()
def models():
    """List available embedding models."""
    from lsearch.embedding import EmbeddingManager

    models = EmbeddingManager.list_models()

    table = Table(title="Available Embedding Models")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Dimension", style="yellow")
    table.add_column("Description", style="white")

    for key, info in models.items():
        table.add_row(key, info["name"], str(info["dim"]), info["description"])

    console.print(table)


if __name__ == "__main__":
    main()
