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


def list_existing_configs() -> list[Path]:
    """List all existing knowledge base configs in parent directories."""
    configs = []
    cwd = Path.cwd()

    # Check current and parent directories
    for parent in [cwd] + list(cwd.parents):
        config_file = parent / ".lsearch" / "config.yaml"
        if config_file.exists():
            try:
                config = Config.from_file(config_file)
                configs.append((parent, config))
            except Exception:
                pass

    return configs


def display_existing_configs(configs: list[tuple[Path, Config]]):
    """Display existing configurations in a table."""
    if not configs:
        return

    console.print()
    table = Table(title="📚 Existing Knowledge Bases")
    table.add_column("#", style="cyan", justify="center")
    table.add_column("Name", style="green")
    table.add_column("Directory", style="dim")
    table.add_column("Paths", style="yellow")
    table.add_column("Model", style="magenta")

    for i, (path, config) in enumerate(configs, 1):
        paths_str = ", ".join([p.path for p in config.paths[:2]])
        if len(config.paths) > 2:
            paths_str += f" (+{len(config.paths) - 2} more)"

        # Truncate path if too long
        path_str = str(path)
        if len(path_str) > 40:
            path_str = "..." + path_str[-37:]

        table.add_row(
            str(i),
            config.name,
            path_str,
            paths_str,
            config.embedding_model
        )

    console.print(table)
    console.print()


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

    # Check for existing configurations
    existing_configs = list_existing_configs()

    if existing_configs:
        display_existing_configs(existing_configs)

        # Ask what to do
        action = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice(
                    "➕  Create NEW knowledge base",
                    value="new"
                ),
                questionary.Choice(
                    "📝  MODIFY existing knowledge base",
                    value="modify"
                ),
                questionary.Choice(
                    "🗑️  OVERWRITE (delete and recreate)",
                    value="overwrite"
                ),
                questionary.Choice(
                    "❌  Cancel",
                    value="cancel"
                ),
            ],
            default="new"
        ).ask()

        if action == "cancel":
            console.print("\n[dim]Cancelled.[/dim]")
            return

        elif action == "modify":
            # Select which config to modify
            if len(existing_configs) == 1:
                selected_path, selected_config = existing_configs[0]
            else:
                choices = [
                    questionary.Choice(
                        f"{config.name} ({path})",
                        value=(path, config)
                    )
                    for path, config in existing_configs
                ]
                selected = questionary.select(
                    "Which knowledge base do you want to modify?",
                    choices=choices
                ).ask()
                selected_path, selected_config = selected

            run_modify_config(selected_path, selected_config)
            return

        elif action == "overwrite":
            # Select which config to overwrite
            if len(existing_configs) == 1:
                selected_path, selected_config = existing_configs[0]
            else:
                choices = [
                    questionary.Choice(
                        f"{config.name} ({path})",
                        value=(path, config)
                    )
                    for path, config in existing_configs
                ]
                selected = questionary.select(
                    "Which knowledge base do you want to overwrite?",
                    choices=choices
                ).ask()
                selected_path, selected_config = selected

            confirm = questionary.confirm(
                f"Are you sure you want to DELETE '{selected_config.name}' and recreate it?",
                default=False
            ).ask()

            if not confirm:
                console.print("\n[dim]Cancelled.[/dim]")
                return

            # Delete existing config
            config_dir = selected_path / ".lsearch"
            import shutil
            if config_dir.exists():
                shutil.rmtree(config_dir)
            console.print(f"[yellow]🗑️  Deleted existing config: {selected_config.name}[/yellow]\n")

    # Create new configuration
    create_new_config(cwd, default_name)


def run_modify_config(config_path: Path, config: Config):
    """Run modification wizard for an existing config."""
    console.print()
    console.print(Panel(
        f"📝 Modifying: {config.name}",
        border_style="yellow"
    ))

    # What to modify
    field_to_modify = questionary.select(
        "What would you like to modify?",
        choices=[
            questionary.Choice("Name", value="name"),
            questionary.Choice("Documentation Paths", value="paths"),
            questionary.Choice("Embedding Model", value="model"),
            questionary.Choice("Cancel", value="cancel"),
        ]
    ).ask()

    if field_to_modify == "cancel":
        console.print("\n[dim]Cancelled.[/dim]")
        return

    if field_to_modify == "name":
        new_name = questionary.text(
            "New knowledge base name:",
            default=config.name
        ).ask()
        if new_name:
            config.name = new_name

    elif field_to_modify == "paths":
        current_paths = [p.path for p in config.paths]
        paths_str = ", ".join(current_paths)
        new_paths = questionary.text(
            "Documentation paths (comma-separated):",
            default=paths_str
        ).ask()
        if new_paths:
            config.paths = [
                PathConfig(path=p.strip(), session_only=False)
                for p in new_paths.split(",")
            ]

    elif field_to_modify == "model":
        model_choice = questionary.select(
            "Choose embedding model:",
            choices=[
                questionary.Choice(
                    "🌏  bge-small-zh (Chinese)",
                    value="bge-small-zh"
                ),
                questionary.Choice(
                    "🇬🇧  all-MiniLM-L6-v2 (English, small)",
                    value="all-MiniLM-L6-v2"
                ),
                questionary.Choice(
                    "🇬🇧  bge-small-en (English, optimized)",
                    value="bge-small-en"
                ),
            ],
            default=config.embedding_model
        ).ask()
        if model_choice:
            config.embedding_model = model_choice

    # Save modified config
    config_file = config_path / ".lsearch" / "config.yaml"
    config.to_file(config_file)

    console.print()
    console.print(Panel(
        Text("✅ Configuration updated!", justify="center", style="bold green"),
        border_style="green"
    ))

    # Show updated config
    table = Table(title="Updated Configuration")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Name", config.name)
    table.add_row("Paths", ", ".join([p.path for p in config.paths]))
    table.add_row("Model", config.embedding_model)
    console.print(table)


def create_new_config(cwd: Path, default_name: str):
    """Create a new knowledge base configuration."""
    console.print(Panel(
        "➕ Create New Knowledge Base",
        border_style="green"
    ))
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
def list_kbs():
    """List all configured knowledge bases."""
    configs = list_existing_configs()

    if not configs:
        console.print("[yellow]No knowledge bases found.[/yellow]")
        console.print("Run: lsearch init")
        return

    display_existing_configs(configs)


@main.command()
@click.argument("name")
def switch_kb(name: str):
    """Switch to a different knowledge base by name."""
    configs = list_existing_configs()

    for path, config in configs:
        if config.name == name:
            console.print(f"[green]Switched to knowledge base: {name}[/green]")
            console.print(f"Location: {path}")
            return

    console.print(f"[red]Knowledge base '{name}' not found.[/red]")
    console.print("Run 'lsearch list-kbs' to see available knowledge bases.")


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
