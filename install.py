#!/usr/bin/env python3
"""Install script for lsearch Claude Code plugin."""

import json
import os
import subprocess
import sys
from pathlib import Path


def get_claude_dir() -> Path:
    """Get Claude Code configuration directory."""
    home = Path.home()
    return home / ".claude"


def get_settings_path() -> Path:
    """Get Claude settings.json path."""
    return get_claude_dir() / "settings.json"


def install_package():
    """Install lsearch Python package."""
    print("📦 Installing lsearch package...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Failed to install package: {result.stderr}")
        sys.exit(1)
    print("✅ Package installed")


def configure_mcp():
    """Configure MCP server in Claude settings."""
    settings_path = get_settings_path()

    # Load existing settings or create new
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = {}

    # Add MCP server configuration
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    settings["mcpServers"]["lsearch"] = {
        "command": "python",
        "args": ["-m", "lsearch.server"]
    }

    # Save settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print(f"✅ MCP server configured in {settings_path}")


def install_skills():
    """Install Claude skills and commands."""
    claude_dir = get_claude_dir()
    plugin_dir = Path(__file__).parent

    # Install skill
    skills_dir = claude_dir / "skills"
    skills_dir.mkdir(exist_ok=True)

    skill_src = plugin_dir / ".claude" / "skills" / "lsearch"
    skill_dst = skills_dir / "lsearch"

    if skill_src.exists():
        import shutil
        # Create skill directory
        skill_dst.mkdir(exist_ok=True)
        # Copy skill.yaml (required by Claude Code)
        skill_yaml_src = skill_src / "skill.yaml"
        skill_yaml_dst = skill_dst / "skill.yaml"
        if skill_yaml_src.exists():
            shutil.copy2(skill_yaml_src, skill_yaml_dst)
            print(f"✅ Skill installed to {skill_dst}")
        else:
            print(f"⚠️  Warning: skill.yaml not found in {skill_src}")

    # Install commands
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(exist_ok=True)

    commands_src = plugin_dir / ".claude" / "commands"
    if commands_src.exists():
        for cmd_file in commands_src.iterdir():
            if cmd_file.is_file():
                cmd_dst = commands_dir / cmd_file.name
                import shutil
                shutil.copy2(cmd_file, cmd_dst)
        print(f"✅ Commands installed to {commands_dir}")


def main():
    """Main installation function."""
    print("🚀 Installing lsearch Claude Code plugin...\n")

    try:
        install_package()
        configure_mcp()
        install_skills()

        print("\n✨ Installation complete!")
        print("\nNext steps:")
        print("1. Restart Claude Code")
        print("2. In your project directory, run: lsearch init")
        print("3. Start using: lsearch: your query here")

    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
