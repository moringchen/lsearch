"""CLI for lsearch."""

import sys
from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from lsearch.config import Config, PathConfig
from lsearch.server import main as server_main

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """lsearch - Local RAG knowledge base for Claude Code."""
    pass


@main.command()
def server():
    """Run the MCP server (for Claude Code integration)."""
    server_main()


def generate_kb_name(cwd: Path) -> str:
    """Generate knowledge base name from current directory path.

    Uses current dir name by default. If index exists, go up one level
    and combine with hyphen.
    """
    name = cwd.name
    index_dir = Config.get_index_dir(name)

    # If index exists, try to include parent directory
    if index_dir.exists():
        parent = cwd.parent
        if parent.name and parent != cwd:
            name = f"{parent.name}-{name}"

    return name


def run_interactive_init():
    """Run interactive initialization wizard using questionary."""
    cwd = Path.cwd()
    default_name = generate_kb_name(cwd)

    # Header
    console.print()
    console.print(Panel(
        Text("🚀 Welcome to lsearch Setup Wizard", justify="center", style="bold cyan"),
        subtitle="Interactive Knowledge Base Configuration",
        border_style="cyan"
    ))
    console.print(f"\n📁 Current directory: [dim]{cwd}[/dim]\n")

    # Check if already initialized
    existing_config = Config.get_project_config_dir()
    if existing_config:
        console.print(f"[yellow]⚠️  lsearch is already initialized in this project.[/yellow]")
        console.print(f"   Config file: [dim]{existing_config}/config.yaml[/dim]\n")

        reinit = questionary.confirm(
            "Do you want to re-initialize with new settings?",
            default=False
        ).ask()

        if not reinit:
            console.print("\n[dim]Cancelled. Existing configuration preserved.[/dim]")
            return
        console.print()

    # Step 1: Knowledge Base Name
    console.print(Panel(
        "Step 1/4: Knowledge Base Name",
        border_style="blue"
    ))

    name = questionary.text(
        "What would you like to name your knowledge base?",
        default=default_name,
        instruction="This identifies your documentation collection"
    ).ask()

    if not name:
        name = default_name
    console.print(f"[green]✓[/green] Name: [cyan]{name}[/cyan]\n")

    # Step 2: Documentation Paths
    console.print(Panel(
        "Step 2/4: Documentation Paths",
        border_style="blue"
    ))

    path_options = [
        "./docs (Documentation folder - RECOMMENDED)",
        "./README.md (Main readme file)",
        "./src (Source code directory)",
        "Multiple paths (custom)",
    ]

    selected_paths = questionary.checkbox(
        "Select directories/files to index (use ↑↓ to navigate, Space to select, Enter to confirm):",
        choices=path_options,
        default=[path_options[0]]
    ).ask()

    if not selected_paths:
        selected_paths = ["./docs (Documentation folder - RECOMMENDED)"]

    # Parse selected paths
    paths = []
    for p in selected_paths:
        if p.startswith("./docs"):
            paths.append("./docs")
        elif p.startswith("./README"):
            paths.append("./README.md")
        elif p.startswith("./src"):
            paths.append("./src")
        elif p.startswith("Multiple"):
            # Custom paths
            custom = questionary.text(
                "Enter paths separated by commas:",
                default="./docs,./README.md",
                instruction="Example: ./docs,./README.md,./notes"
            ).ask()
            if custom:
                paths.extend([p.strip() for p in custom.split(",")])

    # Remove duplicates while preserving order
    seen = set()
    paths = [p for p in paths if not (p in seen or seen.add(p))]

    console.print(f"[green]✓[/green] Paths: [cyan]{', '.join(paths)}[/cyan]\n")

    # Step 3: Embedding Model
    console.print(Panel(
        "Step 3/4: Embedding Model",
        border_style="blue"
    ))

    model_choice = questionary.select(
        "Choose an embedding model for semantic search:",
        choices=[
            questionary.Choice(
                "🌏  bge-small-zh  ~300MB  [Chinese-optimized, Best for Chinese docs]",
                value="bge-small-zh"
            ),
            questionary.Choice(
                "🇬🇧  all-MiniLM-L6-v2  ~70MB  [Small & fast, English general purpose]",
                value="all-MiniLM-L6-v2"
            ),
            questionary.Choice(
                "🇬🇧  bge-small-en  ~130MB  [English-optimized]",
                value="bge-small-en"
            ),
        ],
        default="bge-small-zh"
    ).ask()

    model = model_choice or "bge-small-zh"
    console.print(f"[green]✓[/green] Model: [cyan]{model}[/cyan]\n")

    # Step 4: Confirmation
    console.print(Panel(
        "Step 4/4: Confirm Configuration",
        border_style="blue"
    ))

    summary = f"""[bold]Configuration Summary:[/bold]

  Knowledge Base Name: [cyan]{name}[/cyan]
  Documentation Paths: [cyan]{', '.join(paths)}[/cyan]
  Embedding Model:     [cyan]{model}[/cyan]
  Config Location:     [dim]{cwd}/.lsearch/config.yaml[/dim]
"""
    console.print(summary)

    confirm = questionary.confirm(
        "Create this configuration?",
        default=True
    ).ask()

    if not confirm:
        console.print("\n[dim]Cancelled. No changes made.[/dim]")
        return

    # Create configuration
    try:
        config = Config(
            name=name,
            paths=[PathConfig(path=p, session_only=False) for p in paths],
            embedding_model=model,
        )

        config_dir = cwd / ".lsearch"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.yaml"

        config.to_file(config_file)

        # Success message
        console.print()
        console.print(Panel(
            Text("✅ lsearch initialized successfully!", justify="center", style="bold green"),
            border_style="green"
        ))

        console.print(f"""
[bold]📋 Configuration:[/bold]
  Knowledge base name: [cyan]{name}[/cyan]
  Documentation paths: [cyan]{', '.join(paths)}[/cyan]
  Embedding model:     [cyan]{model}[/cyan]
  Config file:         [dim]{config_file}[/dim]

[bold]🚀 Next Steps:[/bold]
  1. Create your documentation directory:
     [dim]mkdir -p {' '.join(paths)}[/dim]

  2. Add markdown files to your docs

  3. Index your documents (in Claude Code):
     [dim]/lsearch-index[/dim]

  4. Start searching:
     [dim]/lsearch your search query[/dim]

[bold]📚 Available Commands:[/bold]
  • /lsearch <query>      Search knowledge base
  • /lsearch-index        Index documents
  • /lsearch-fetch <url>  Fetch and index web page
  • /lsearch-add <path>   Add temporary path
  • /lsearch-stats        Show statistics
  • /kb <query>           Force search knowledge base
""")

    except Exception as e:
        console.print(f"\n[red]❌ Error creating configuration: {e}[/red]")
        console.print("[dim]Please check permissions and try again.[/dim]")


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
@click.option(
    "--interactive/--no-interactive",
    default=True,
    help="Use interactive wizard (default: True)",
)
def init(name: str | None, path: tuple, model: str, interactive: bool):
    """Initialize a new knowledge base configuration."""

    # Use interactive wizard by default
    if interactive:
        run_interactive_init()
        return

    # Non-interactive mode (for scripting)
    if name is None:
        cwd = Path.cwd()
        name = generate_kb_name(cwd)

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
        console.print("[yellow]No knowledge base configured in this directory.[/yellow]")
        console.print("Run: lsearch init")
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

    # Show index stats
    index_dir = Config.get_index_dir(config.name)
    if index_dir.exists():
        console.print(f"\n[bold]Index Location:[/bold] {index_dir}")
    else:
        console.print("\n[yellow]No index created yet. Run:[/yellow]")
        console.print("  lsearch index")


@main.command()
@click.option("--path", help="Specific path to index")
def index(path: str | None):
    """Index the knowledge base."""
    console.print("[yellow]Indexing is done through the MCP server.[/yellow]")
    console.print("Run this command from Claude Code, or use:")
    console.print("  lsearch server")


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
