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

lsearch 是 Claude Code 的本地 RAG (Retrieval-Augmented Generation) 插件，支持语义搜索 + BM25 关键词搜索的混合检索。

## 触发方式

- `lsearch: <查询内容>` - 自动触发知识库搜索
- `@kb <查询内容>` - 强制触发知识库搜索

## 命令

| 命令 | 功能 |
|------|------|
| `/lsearch-index` | 手动触发索引更新 |
| `/lsearch-fetch <url>` | 抓取网页并加入知识库 |
| `/lsearch-add <路径>` | 添加临时知识库路径（会话级）|
| `/lsearch-stats` | 查看知识库统计 |

## 工作原理

1. **索引阶段**：将 Markdown 文件分块，生成向量嵌入（本地模型）和 BM25 索引
2. **检索阶段**：混合检索（语义 + 关键词）+ RRF 融合排序
3. **链接扩展**：自动包含相关笔记的链接内容
4. **上下文控制**：默认 4000 tokens，超长时提示选择

## 配置

项目根目录创建 `.lsearch/config.yaml`：

```yaml
name: my-project
paths:
  - ./docs
  - ./README.md
exclude:
  - node_modules/**
  - .git/**
embedding_model: all-MiniLM-L6-v2  # 或 bge-small-zh
token_limit: 4000
auto_expand_links: true
```

## 安装

```bash
pip install lsearch
```

然后在 `~/.claude/settings.json` 添加：

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

## 特性

- 🔍 混合检索（向量 + BM25）
- 🔗 Obsidian 风格链接支持
- 🌐 网页抓取（API 文档、Swagger）
- 💾 本地小模型（70MB-300MB）
- 🚀 纯本地运行，无云端依赖
