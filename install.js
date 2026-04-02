#!/usr/bin/env node

/**
 * lsearch installer for npx
 * This script installs lsearch Python package and configures Claude Code integration
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const Colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m'
};

function log(message, color = Colors.reset) {
  console.log(`${color}${message}${Colors.reset}`);
}

function runCommand(command, description) {
  log(`\n${description}...`, Colors.cyan);
  try {
    execSync(command, { stdio: 'inherit', cwd: __dirname });
    return true;
  } catch (error) {
    log(`Failed: ${error.message}`, Colors.red);
    return false;
  }
}

function main() {
  log('\n' + '='.repeat(60), Colors.bright);
  log('lsearch Installer', Colors.bright);
  log('Local RAG knowledge base for Claude Code', Colors.cyan);
  log('='.repeat(60) + '\n', Colors.bright);

  // Check Python version
  log('Checking Python version...', Colors.cyan);
  try {
    const pythonVersion = execSync('python3 --version', { encoding: 'utf8' }).trim();
    log(`Found: ${pythonVersion}`, Colors.green);
  } catch (error) {
    log('Python 3 not found. Please install Python 3.10 or higher.', Colors.red);
    process.exit(1);
  }

  // Install Python package
  if (!runCommand('pip3 install -e ".[dev]"', 'Installing lsearch Python package')) {
    log('Failed to install Python package. You may need to run with sudo.', Colors.red);
    process.exit(1);
  }

  // Configure Claude Code
  log('\nConfiguring Claude Code integration...', Colors.cyan);

  const claudeDir = path.join(os.homedir(), '.claude');
  const settingsFile = path.join(claudeDir, 'settings.json');

  // Ensure .claude directory exists
  if (!fs.existsSync(claudeDir)) {
    fs.mkdirSync(claudeDir, { recursive: true });
  }

  // Read existing settings or create new
  let settings = {};
  if (fs.existsSync(settingsFile)) {
    try {
      settings = JSON.parse(fs.readFileSync(settingsFile, 'utf8'));
    } catch (e) {
      settings = {};
    }
  }

  // Add MCP server configuration
  settings.mcpServers = settings.mcpServers || {};
  settings.mcpServers.lsearch = {
    command: 'python3',
    args: ['-m', 'lsearch.server']
  };

  // Write settings
  fs.writeFileSync(settingsFile, JSON.stringify(settings, null, 2));
  log('✓ Claude Code MCP server configured', Colors.green);

  // Copy slash commands
  const commandsSrc = path.join(__dirname, '.claude', 'commands');
  const commandsDst = path.join(claudeDir, 'commands');

  if (fs.existsSync(commandsSrc)) {
    if (!fs.existsSync(commandsDst)) {
      fs.mkdirSync(commandsDst, { recursive: true });
    }

    const commandFiles = fs.readdirSync(commandsSrc).filter(f => f.endsWith('.md'));
    for (const file of commandFiles) {
      const src = path.join(commandsSrc, file);
      const dst = path.join(commandsDst, file);
      fs.copyFileSync(src, dst);
    }
    log(`✓ Copied ${commandFiles.length} slash commands`, Colors.green);
  }

  // Copy skills
  const skillsSrc = path.join(__dirname, '.claude', 'skills', 'lsearch');
  const skillsDst = path.join(claudeDir, 'skills', 'lsearch');

  if (fs.existsSync(skillsSrc)) {
    if (!fs.existsSync(skillsDst)) {
      fs.mkdirSync(skillsDst, { recursive: true });
    }

    const skillFiles = fs.readdirSync(skillsSrc);
    for (const file of skillFiles) {
      const src = path.join(skillsSrc, file);
      const dst = path.join(skillsDst, file);
      if (fs.statSync(src).isFile()) {
        fs.copyFileSync(src, dst);
      }
    }
    log('✓ Copied skill definition', Colors.green);
  }

  // Success message
  log('\n' + '='.repeat(60), Colors.bright);
  log('Installation Complete!', Colors.green);
  log('='.repeat(60), Colors.bright);
  log('\nAvailable commands:', Colors.bright);
  log('  lsearch init         - Initialize knowledge base (REQUIRED FIRST)', Colors.green);
  log('  /lsearch <query>     - Search knowledge base (in Claude Code)', Colors.cyan);
  log('  /lsearch-index       - Index documents (in Claude Code)', Colors.cyan);
  log('  /lsearch-fetch <url> - Fetch and index URL (in Claude Code)', Colors.cyan);
  log('  /lsearch-add <path>  - Add path to knowledge base (in Claude Code)', Colors.cyan);
  log('  /lsearch-stats       - Show statistics (in Claude Code)', Colors.cyan);
  log('  /kb <query>          - Force search knowledge base (in Claude Code)', Colors.cyan);
  log('\nQuick start:', Colors.bright);
  log('  1. In your project terminal, run: lsearch init', Colors.yellow);
  log('  2. In Claude Code, index docs: /lsearch-index', Colors.yellow);
  log('  3. Start searching: /lsearch your query', Colors.yellow);
  log('\nPlease restart Claude Code to load the new commands.', Colors.yellow);
  log('='.repeat(60) + '\n', Colors.bright);
}

if (require.main === module) {
  main();
}

module.exports = { main };
