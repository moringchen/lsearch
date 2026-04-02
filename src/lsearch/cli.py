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
@click.version_option(version="0.2.0")
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
    table = Table(title="[bold]Existing Knowledge Bases[/bold]")
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
        Text("lsearch Setup", justify="center", style="bold"),
        border_style="cyan"
    ))
    console.print(f"\nCurrent directory: [dim]{cwd}[/dim]\n")

    # Check for existing configurations
    existing_configs = list_existing_configs()

    if existing_configs:
        display_existing_configs(existing_configs)

        # Ask what to do
        action = questionary.select(
            "Choose an action:",
            choices=[
                questionary.Choice("+ Create new knowledge base", value="new"),
                questionary.Choice("~ Modify existing knowledge base", value="modify"),
            ],
            default="new"
        ).ask()

        if action == "modify":
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

    # Create new configuration
    create_new_config(cwd, default_name)


def run_modify_config(config_path: Path, config: Config):
    """Run modification wizard for an existing config."""
    console.print()
    console.print(Panel(
        f"Modify: {config.name}",
        border_style="yellow"
    ))

    # What to modify
    field_to_modify = questionary.select(
        "What would you like to modify?",
        choices=[
            questionary.Choice("Name", value="name"),
            questionary.Choice("Documentation Paths", value="paths"),
            questionary.Choice("Embedding Model", value="model"),
        ]
    ).ask()

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
                    "bge-small-zh (Chinese)",
                    value="bge-small-zh"
                ),
                questionary.Choice(
                    "all-MiniLM-L6-v2 (English, small)",
                    value="all-MiniLM-L6-v2"
                ),
                questionary.Choice(
                    "bge-small-en (English, optimized)",
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
        "[bold]Configuration updated[/bold]",
        border_style="green"
    ))

    # Show updated config
    table = Table()
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Name", config.name)
    table.add_row("Paths", ", ".join([p.path for p in config.paths]))
    table.add_row("Model", config.embedding_model)
    console.print(table)


def create_new_config(cwd: Path, default_name: str):
    """Create a new knowledge base configuration using form-style prompts."""
    console.print()
    console.print("[bold]Create New Knowledge Base[/bold]")
    console.print()

    # Step 1: Knowledge Base Name
    name = questionary.text(
        "Knowledge base name:",
        default=default_name
    ).ask()

    if not name:
        name = default_name

    # Step 2: Documentation Paths - use dictionary to separate display from value
    path_choices = {
        "./docs": "./docs (Documentation folder)",
        "./README.md": "./README.md (Main readme)",
        "./src": "./src (Source code)",
        "custom": "Other paths (custom)",
    }

    selected = questionary.checkbox(
        "Select paths to index (Space=select, Enter=confirm):",
        choices=[
            questionary.Choice(display, value=key)
            for key, display in path_choices.items()
        ],
        default=["./docs"]
    ).ask()

    if not selected:
        selected = ["./docs"]

    # Parse selected paths
    paths = []
    for key in selected:
        if key == "custom":
            custom = questionary.text(
                "Enter paths (comma-separated):",
                default="./docs,./README.md"
            ).ask()
            if custom:
                paths.extend([p.strip() for p in custom.split(",")])
        else:
            paths.append(key)

    # Remove duplicates while preserving order
    seen = set()
    paths = [p for p in paths if not (p in seen or seen.add(p))]

    # Step 3: Embedding Model
    model_choice = questionary.select(
        "Embedding model:",
        choices=[
            questionary.Choice("bge-small-zh ~300MB (Chinese)", value="bge-small-zh"),
            questionary.Choice("all-MiniLM-L6-v2 ~70MB (English)", value="all-MiniLM-L6-v2"),
            questionary.Choice("bge-small-en ~130MB (English)", value="bge-small-en"),
        ],
        default="bge-small-zh"
    ).ask()

    model = model_choice or "bge-small-zh"

    # Step 4: Confirmation (single-page form summary)
    console.print()
    console.print("[bold]Configuration Summary:[/bold]")
    console.print(f"  Name:  {name}")
    console.print(f"  Paths: {', '.join(paths)}")
    console.print(f"  Model: {model}")
    console.print()

    confirm = questionary.confirm("Create configuration?", default=True).ask()

    if not confirm:
        console.print("Cancelled.")
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
        console.print("[bold]Configuration created[/bold]")
        console.print()
        console.print(f"  Name:  {name}")
        console.print(f"  Paths: {', '.join(paths)}")
        console.print(f"  Model: {model}")
        console.print(f"  File:  {config_file}")
        console.print()
        console.print("Next steps:")
        console.print(f"  1. mkdir -p {' '.join(paths)}")
        console.print("  2. Add markdown files")
        console.print("  3. In Claude Code: /lsearch-index")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


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
