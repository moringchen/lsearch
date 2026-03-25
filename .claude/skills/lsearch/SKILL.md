---
name: lsearch
description: Local RAG knowledge base for Claude Code - search your project docs with semantic + keyword hybrid search
tools:
  - mcp__lsearch__search
  - mcp__lsearch__search_with_context
  - mcp__lsearch__index
  - mcp__lsearch__fetch_url
  - mcp__lsearch__add_path
  - mcp__lsearch__list_paths
  - mcp__lsearch__get_stats
---

# lsearch - Local Knowledge Base

**English** | [中文](#中文说明)

---

## Overview

lsearch is a local RAG (Retrieval-Augmented Generation) plugin for Claude Code, supporting hybrid semantic + BM25 keyword search.

## Trigger Methods

| Method | Description | Example |
|--------|-------------|---------|
| `lsearch: <query>` | Automatically trigger knowledge base search | `lsearch: How does auth work?` |
| `@kb <query>` | Force trigger knowledge base search | `@kb deployment process` |

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/lsearch <query>` | Search knowledge base via slash command | `/lsearch API documentation` |
| `/lsearch-index` | Manually trigger index update | `/lsearch-index` |
| `/lsearch-fetch <url>` | Fetch and add web page to knowledge base | `/lsearch-fetch https://docs.example.com` |
| `/lsearch-add <path>` | Add temporary knowledge base path (session-level) | `/lsearch-add ~/notes` |
| `/lsearch-stats` | Show knowledge base statistics | `/lsearch-stats` |

## How It Works

```
Markdown Files → Chunks → Vector Index (Chroma) + BM25 Index + Link Graph
                                              ↓
                                    Hybrid Search (RRF Fusion)
                                              ↓
                                     Context Builder → Claude
```

1. **Indexing Phase**: Markdown files are split into chunks, vector embeddings (local model) and BM25 index are generated
2. **Search Phase**: Hybrid search (semantic + keyword) + RRF fusion ranking
3. **Link Expansion**: Automatically include linked note content
4. **Context Control**: Default 4000 tokens, prompt for selection if exceeded

## Configuration

Create `.lsearch/config.yaml` in your project root:

```yaml
name: my-project
paths:
  - ./docs
  - ./README.md
  - ./src
exclude:
  - node_modules/**
  - .git/**
  - "*.tmp"
embedding_model: all-MiniLM-L6-v2  # or bge-small-zh for Chinese
token_limit: 4000
auto_expand_links: true
chunk_size: 500
chunk_overlap: 50
```

### Embedding Models

| Model | Size | Best For |
|-------|------|----------|
| `all-MiniLM-L6-v2` | 70MB | English general purpose |
| `bge-small-zh` | 300MB | Chinese optimized |
| `bge-small-en` | 130MB | English optimized |

## Installation

### Option 1: Claude Code Plugin (Recommended)

```bash
git clone https://github.com/moringchen/lsearch.git ~/.claude/plugins/lsearch
cd ~/.claude/plugins/lsearch && python install.py
```

### Option 2: PyPI

```bash
pip install lsearch
```

Then add to `~/.claude/settings.json`:

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

## Features

- 🔍 **Hybrid Search**: Semantic (vector) + BM25 keyword + RRF fusion
- 🔗 **Link Graph**: Obsidian-style bidirectional links
- 🌐 **Web Fetching**: Index API docs, Swagger specs
- 🤖 **Local Models**: 70-300MB embedding models
- 💾 **Pure Local**: No cloud dependencies

## CLI Usage

```bash
# Initialize knowledge base
lsearch init --name my-project --path ./docs

# Add paths
lsearch add-path ./more-docs

# Check status
lsearch status

# List available models
lsearch models
```

---

## 中文说明

### 概述

lsearch 是 Claude Code 的本地 RAG（检索增强生成）插件，支持语义搜索 + BM25 关键词搜索的混合检索。

### 触发方式

| 方式 | 说明 | 示例 |
|--------|-------------|---------|
| `lsearch: <查询>` | 自动触发知识库搜索 | `lsearch: 认证如何工作？` |
| `@kb <查询>` | 强制触发知识库搜索 | `@kb 部署流程` |

### 可用命令

| 命令 | 说明 | 示例 |
|---------|-------------|---------|
| `/lsearch <查询>` | 通过斜杠命令搜索 | `/lsearch API 文档` |
| `/lsearch-index` | 手动触发索引更新 | `/lsearch-index` |
| `/lsearch-fetch <url>` | 抓取网页并加入知识库 | `/lsearch-fetch https://docs.example.com` |
| `/lsearch-add <路径>` | 添加临时知识库路径（会话级） | `/lsearch-add ~/notes` |
| `/lsearch-stats` | 显示知识库统计信息 | `/lsearch-stats` |

### 工作原理

```
Markdown 文件 → 分块 → 向量索引 (Chroma) + BM25 索引 + 链接图谱
                                              ↓
                                    混合搜索 (RRF 融合)
                                              ↓
                                     上下文构建 → Claude
```

1. **索引阶段**：将 Markdown 文件分块，生成向量嵌入（本地模型）和 BM25 索引
2. **检索阶段**：混合检索（语义 + 关键词）+ RRF 融合排序
3. **链接扩展**：自动包含相关笔记的链接内容
4. **上下文控制**：默认 4000 tokens，超长时提示选择

### 配置

在项目根目录创建 `.lsearch/config.yaml`：

```yaml
name: my-project
paths:
  - ./docs
  - ./README.md
  - ./src
exclude:
  - node_modules/**
  - .git/**
  - "*.tmp"
embedding_model: all-MiniLM-L6-v2  # 或 bge-small-zh（中文）
token_limit: 4000
auto_expand_links: true
chunk_size: 500
chunk_overlap: 50
```

### 嵌入模型

| 模型 | 大小 | 适用场景 |
|-------|------|----------|
| `all-MiniLM-L6-v2` | 70MB | 英文通用 |
| `bge-small-zh` | 300MB | 中文优化 |
| `bge-small-en` | 130MB | 英文优化 |

### 安装

#### 方式 1：Claude Code 插件（推荐）

```bash
git clone https://github.com/moringchen/lsearch.git ~/.claude/plugins/lsearch
cd ~/.claude/plugins/lsearch && python install.py
```

#### 方式 2：PyPI

```bash
pip install lsearch
```

然后在 `~/.claude/settings.json` 中添加：

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

### 特性

- 🔍 **混合检索**：语义（向量）+ BM25 关键词 + RRF 融合
- 🔗 **链接图谱**：Obsidian 风格的双向链接
- 🌐 **网页抓取**：索引 API 文档、Swagger 规范
- 🤖 **本地模型**：70-300MB 嵌入模型
- 💾 **纯本地**：无云端依赖

### CLI 使用

```bash
# 初始化知识库
lsearch init --name my-project --path ./docs

# 添加路径
lsearch add-path ./more-docs

# 检查状态
lsearch status

# 列出可用模型
lsearch models
```
