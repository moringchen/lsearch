# lsearch

[![PyPI version](https://badge.fury.io/py/lsearch.svg)](https://badge.fury.io/py/lsearch)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | **中文**

为 Claude Code 打造的本地 RAG（检索增强生成）知识库。使用混合语义 + 关键词搜索来检索项目文档。

## 功能特性

- 🔍 **混合搜索** - 结合语义向量搜索（Chroma）和 BM25 关键词搜索
- 🔗 **链接图谱** - 支持 Obsidian 风格的双向链接，自动展开相关笔记
- 🌐 **网页抓取** - 下载并索引 API 文档、Swagger 规范
- 🤖 **本地模型** - 使用小型嵌入模型（70-300MB），无需云端依赖
- ⚡ **快速响应** - 纯本地运行，索引热加载
- 📝 **智能上下文** - 基于 Token 的上下文构建，支持交互式选择
- 🎯 **多种触发方式** - 支持 `lsearch:`、`@kb` 或斜杠命令
- 🎯 **关键词自动触发** - 智能检测知识查询意图

## 安装

### 方式 1：Claude Code 插件（推荐）

作为 Claude Code 插件安装，自动配置 MCP：

```bash
# 克隆到 Claude 插件目录
git clone https://github.com/moringchen/lsearch.git ~/.claude/plugins/lsearch

# 运行安装脚本
cd ~/.claude/plugins/lsearch && python install.py
```

然后重启 Claude Code。

### 方式 2：PyPI 安装

```bash
pip install lsearch
```

然后手动添加到 `~/.claude/settings.json`：

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

### 方式 3：Skills CLI (npx skills)

通过 Skills CLI 从 [skills.sh](https://skills.sh) 安装：

```bash
# 安装 lsearch skill
npx skills add moringchen/lsearch -g

# 或通过 PyPI 安装
npx skills add moringchen/lsearch@pip -g
```

`-g` 标志表示全局安装（用户级别）。

### 方式 4：开发安装

```bash
git clone https://github.com/moringchen/lsearch.git
cd lsearch
pip install -e ".[dev]"
```

## 快速开始

### 1. 初始化知识库

```bash
# 在你的项目目录中
# 自动根据目录生成名称，默认使用 ./docs 路径
lsearch init

# 或自定义名称和路径
lsearch init --name my-project --path ./docs --path ./README.md
```

**自动生成的名称：**
- 如果在 `/home/user/projects/my-app` 中运行，名称将为：`my-app`
- 如果 `my-app` 已存在，名称将为：`projects-my-app`

这会创建 `.lsearch/config.yaml`：

```yaml
name: my-project
paths:
  - path: ./docs
    session_only: false
  - path: ./README.md
    session_only: false
embedding_model: bge-small-zh  # 默认：中文优化
token_limit: 4000
auto_expand_links: true
```

### 2. 在 Claude Code 中使用

配置完成后，在 Claude Code 中使用以下触发方式：

| 触发方式 | 说明 | 示例 |
|---------|------|------|
| `lsearch: <查询>` | 自动触发 RAG 搜索 | `lsearch: 认证如何工作？` |
| `@kb <查询>` | 强制触发知识库搜索 | `@kb 部署流程` |
| **关键词触发** | 特定关键词自动触发 | 见下方 |
| `/lsearch <查询>` | 通过斜杠命令搜索 | `/lsearch API 文档` |
| `/lsearch-index` | 手动触发索引 | `/lsearch-index` |
| `/lsearch-fetch <url>` | 抓取并索引网页 | `/lsearch-fetch https://docs.example.com` |
| `/lsearch-add <路径>` | 为当前会话添加临时路径 | `/lsearch-add ~/notes` |
| `/lsearch-stats` | 显示知识库统计信息 | `/lsearch-stats` |

### 关键词自动触发

当用户问题包含特定关键词时，自动搜索知识库：

**触发关键词：**
- 文档相关："docs", "documentation", "文档"
- 架构相关："architecture", "设计", "架构"
- API相关："api", "interface", "接口"
- 部署相关："deploy", "deployment", "部署"
- 配置相关："config", "configuration", "配置"
- 流程相关："how to", "流程", "怎么", "如何"

**自动触发示例：**
- "What's the deployment process?" → 自动搜索
- "怎么配置数据库？" → 自动搜索
- "API documentation" → 自动搜索
- "项目架构是什么样的？" → 自动搜索

**工作原理：**
1. 检测用户查询中的关键词
2. 自动调用 `mcp__lsearch__search_with_context`
3. 将结果包含在回复中

## 工作原理

```
Markdown 文件 → 分块 → 向量索引 (Chroma) + BM25 索引 + 链接图谱
                                              ↓
                                    混合搜索 (RRF 融合)
                                              ↓
                                     上下文构建 → Claude
```

### 索引流程

1. **文档处理** - 解析 Markdown 文件，提取 frontmatter，识别 wiki 链接
2. **分块** - 将文档分割为重叠的块（默认 500 字）
3. **嵌入** - 使用本地模型为每个块生成嵌入（all-MiniLM-L6-v2 或 bge-small-zh）
4. **索引** - 存储到 Chroma（向量）+ Whoosh（BM25）+ NetworkX（链接图谱）

### 搜索流程

1. **向量搜索** - 使用余弦距离进行语义相似度匹配
2. **BM25 搜索** - 基于词频的关键词匹配
3. **RRF 融合** - 倒数排序融合合并两种结果
4. **链接展开** - 如启用，包含链接的笔记
5. **上下文构建** - 在 Token 限制内组装结果

## 配置

### 配置文件 (`.lsearch/config.yaml`)

```yaml
name: my-project                          # 知识库名称
paths:                                    # 要索引的路径
  - path: ./docs
    session_only: false
  - path: ./README.md
    session_only: false
exclude:                                  # 排除模式
  - node_modules/**
  - .git/**
  - "*.tmp"
embedding_model: bge-small-zh             # 嵌入模型（默认：中文优化）
token_limit: 4000                         # 每次查询最大 Token 数
auto_expand_links: true                   # 包含链接的笔记
chunk_size: 500                           # 每块字数
chunk_overlap: 50                         # 块之间重叠字数
```

### 嵌入模型

| 模型 | 大小 | 适用场景 | 语言 | 默认 |
|------|------|----------|------|------|
| `bge-small-zh` | 300MB | 中文优化 | 中文 | ✅ 默认 |
| `all-MiniLM-L6-v2` | 70MB | 通用场景 | 英文 | |
| `bge-small-en` | 130MB | 英文优化 | 英文 | |

## CLI 命令

```bash
# 初始化知识库
lsearch init --name my-project --path ./docs

# 向现有知识库添加路径
lsearch add-path ./more-docs

# 检查状态和统计信息
lsearch status

# 列出可用的嵌入模型
lsearch models

# 运行 MCP 服务器（用于 Claude Code 集成）
lsearch server
```

## 使用示例

### 示例 1：项目文档设置

```bash
# 进入你的项目目录
cd ~/projects/my-web-app

# 使用默认设置初始化（自动生成名称，./docs 路径）
lsearch init

# 创建 docs 目录并添加文件
mkdir -p docs
echo "# API 文档" > docs/api.md
echo "# 部署指南" > docs/deployment.md

# 在 Claude Code 中索引文档
/lsearch-index

# 搜索你的文档
lsearch: 如何部署这个项目？
```

### 示例 2：多语言项目

```bash
# 使用中文优化模型初始化（默认）
lsearch init --name backend-api

# 添加多个文档路径
lsearch init --name fullstack \
  --path ./backend/docs \
  --path ./frontend/docs \
  --path ./README.md \
  --model bge-small-zh
```

### 示例 3：网页文档

```bash
# 抓取并索引外部 API 文档
/lsearch-fetch https://docs.example.com/api

# 搜索抓取的文档
@kb example API 认证
```

### 示例 4：临时知识库

```bash
# 只为当前会话添加临时路径
/lsearch-add ~/personal-notes/project-ideas.md

# 搜索包括项目文档和临时笔记
lsearch: 项目需求是什么？
```

### 示例 5：多项目知识库

```yaml
# .lsearch/config.yaml
name: work-projects
paths:
  - path: ~/work/project-a/docs
    session_only: false
  - path: ~/work/project-b/docs
    session_only: false
  - path: ~/work/shared-guides
    session_only: false
exclude:
  - "**/node_modules/**"
  - "**/.git/**"
embedding_model: bge-small-zh
token_limit: 4000
```

## 网页抓取

抓取并索引网页文档：

```
/lsearch-fetch https://docs.python.org/3/library/asyncio.html
```

支持：
- **HTML** → Markdown 转换
- **Swagger/OpenAPI JSON** → Markdown
- **自动标题提取**

抓取的文档存储在 `~/.lsearch/fetched/` 并自动索引。

## 项目结构

```
lsearch/
├── src/lsearch/
│   ├── server.py              # MCP 服务器（主入口）
│   ├── cli.py                 # CLI 命令
│   ├── config.py              # 配置管理
│   ├── embedding.py           # 嵌入模型
│   ├── document_processor.py  # Markdown 处理
│   ├── fetcher.py             # URL 抓取
│   ├── indexers/
│   │   ├── chroma_indexer.py  # 向量数据库（Chroma）
│   │   ├── bm25_indexer.py    # 关键词索引（Whoosh）
│   │   └── link_graph.py      # 笔记关系（NetworkX）
│   └── search/
│       ├── hybrid_search.py   # RRF 融合
│       └── context_builder.py # Token 管理
├── .claude/
│   ├── commands/              # 斜杠命令
│   └── skills/                # Skill 定义
├── skill/
│   └── SKILL.md               # Claude Code skill 定义
├── install.py                 # 安装脚本
├── README.md                  # 英文文档
├── README.zh.md               # 中文文档
└── pyproject.toml             # 包配置
```

## 开发

```bash
# 安装依赖
pip install -e ".[dev]"

# 格式化代码
black src/ tests/
ruff check src/ tests/

# 运行测试
pytest

# 类型检查
mypy src/
```

## 故障排除

### 问题：MCP 服务器无法启动

**解决方案**：检查 lsearch 是否已安装：
```bash
python -m lsearch.server --version
```

如果未安装，运行：
```bash
pip install lsearch
```

### 问题：没有搜索结果

**解决方案**：确保文档已索引：
```bash
/lsearch-index
```

或检查索引状态：
```bash
/lsearch-stats
```

### 问题：模型下载失败

**解决方案**：嵌入模型在首次使用时下载。确保你有：
- 网络连接（仅首次）
- ~300MB 磁盘空间（中文模型）或 ~70MB（英文模型）

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)

## 贡献

欢迎贡献！请提交 Issue 或 PR。

## 致谢

- [Chroma](https://www.trychroma.com/) - 向量数据库
- [Whoosh](https://whoosh.readthedocs.io/) - BM25 索引
- [sentence-transformers](https://www.sbert.net/) - 嵌入模型
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol

## 联系方式

- GitHub: [@moringchen](https://github.com/moringchen)
- 邮箱: 843115404@qq.com
