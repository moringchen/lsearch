# lsearch - Claude Code Plugin

Local RAG knowledge base for Claude Code with hybrid semantic + keyword search.

**English** | [中文](#中文说明)

---

## Installation

### Method 1: Auto-install (Recommended)

```bash
# Clone to Claude plugins directory
git clone https://github.com/moringchen/lsearch.git ~/.claude/plugins/lsearch

# Run install script
cd ~/.claude/plugins/lsearch && python install.py
```

### Method 2: Manual Install

1. **Clone the repository:**
   ```bash
   git clone https://github.com/moringchen/lsearch.git
   cd lsearch
   ```

2. **Install Python package:**
   ```bash
   pip install -e .
   ```

3. **Configure MCP Server** in `~/.claude/settings.json`:
   ```json
   {
     "mcpServers": {
       "lsearch": {
         "command": "python",
         "args": ["-m", "lsearch.server"]
       }
     }
   }
   ```

4. **Copy skill and commands** (optional):
   ```bash
   cp -r .claude/skills/lsearch ~/.claude/skills/
   cp -r .claude/commands/* ~/.claude/commands/
   ```

## Quick Start

1. **Initialize knowledge base** in your project:
   ```bash
   lsearch init --name my-project --path ./docs
   ```

2. **Start using in Claude Code:**
   - `lsearch: How does authentication work?`
   - `@kb deployment process`
   - `/lsearch-index`

## Available Commands

| Command | Description |
|---------|-------------|
| `lsearch: <query>` | Search knowledge base (auto-trigger) |
| `@kb <query>` | Force knowledge base search |
| `/lsearch <query>` | Search via command |
| `/lsearch-index` | Index configured paths |
| `/lsearch-fetch <url>` | Fetch and index web page |
| `/lsearch-add <path>` | Add temporary session path |
| `/lsearch-stats` | Show knowledge base stats |

## Configuration

Create `.lsearch/config.yaml` in your project:

```yaml
name: my-project
paths:
  - ./docs
  - ./README.md
  - ./src
exclude:
  - node_modules/**
  - .git/**
embedding_model: all-MiniLM-L6-v2  # or bge-small-zh for Chinese
token_limit: 4000
auto_expand_links: true
```

## How It Works

```
Markdown Files → Chunks → Vector Index (Chroma) + BM25 Index + Link Graph
                                              ↓
                                    Hybrid Search (RRF Fusion)
                                              ↓
                                     Context Builder → Claude
```

## Features

- 🔍 **Hybrid Search**: Semantic (vector) + BM25 keyword + RRF fusion
- 🔗 **Link Graph**: Obsidian-style bidirectional links
- 🌐 **Web Fetching**: Index API docs, Swagger specs
- 🤖 **Local Models**: 70-300MB embedding models
- 💾 **Pure Local**: No cloud dependencies

## Requirements

- Python 3.10+
- Claude Code with MCP support

## License

MIT

---

## 中文说明

### 安装方法

#### 方法 1：自动安装（推荐）

```bash
# 克隆到 Claude 插件目录
git clone https://github.com/moringchen/lsearch.git ~/.claude/plugins/lsearch

# 运行安装脚本
cd ~/.claude/plugins/lsearch && python install.py
```

#### 方法 2：手动安装

1. **克隆仓库：**
   ```bash
   git clone https://github.com/moringchen/lsearch.git
   cd lsearch
   ```

2. **安装 Python 包：**
   ```bash
   pip install -e .
   ```

3. **配置 MCP 服务器**（在 `~/.claude/settings.json`）：
   ```json
   {
     "mcpServers": {
       "lsearch": {
         "command": "python",
         "args": ["-m", "lsearch.server"]
       }
     }
   }
   ```

4. **复制 skill 和命令**（可选）：
   ```bash
   cp -r .claude/skills/lsearch ~/.claude/skills/
   cp -r .claude/commands/* ~/.claude/commands/
   ```

### 快速开始

1. **在项目目录初始化知识库：**
   ```bash
   lsearch init --name my-project --path ./docs
   ```

2. **在 Claude Code 中使用：**
   - `lsearch: 认证如何工作？`
   - `@kb 部署流程`
   - `/lsearch-index`

### 可用命令

| 命令 | 说明 |
|---------|-------------|
| `lsearch: <query>` | 搜索知识库（自动触发） |
| `@kb <query>` | 强制搜索知识库 |
| `/lsearch <query>` | 通过命令搜索 |
| `/lsearch-index` | 索引配置的路径 |
| `/lsearch-fetch <url>` | 抓取并索引网页 |
| `/lsearch-add <path>` | 添加临时会话路径 |
| `/lsearch-stats` | 显示知识库统计信息 |

### 配置

在项目目录创建 `.lsearch/config.yaml`：

```yaml
name: my-project
paths:
  - ./docs
  - ./README.md
  - ./src
exclude:
  - node_modules/**
  - .git/**
embedding_model: all-MiniLM-L6-v2  # 或使用 bge-small-zh（中文）
token_limit: 4000
auto_expand_links: true
```

### 功能特性

- 🔍 **混合搜索**：语义（向量）+ BM25 关键词 + RRF 融合
- 🔗 **链接图谱**：Obsidian 风格的双向链接
- 🌐 **网页抓取**：索引 API 文档、Swagger 规范
- 🤖 **本地模型**：70-300MB 嵌入模型
- 💾 **纯本地**：无云端依赖

### 要求

- Python 3.10+
- 支持 MCP 的 Claude Code

### 许可证

MIT
