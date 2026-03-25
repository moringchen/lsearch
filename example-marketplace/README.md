# Example Marketplace for lsearch

这是一个示例 marketplace 仓库，展示如何为 lsearch 创建自定义 marketplace，用于：

1. **团队内部使用** - 让团队成员通过搜索发现 lsearch
2. **私有分发** - 不依赖 skills.sh 官方索引
3. **测试目的** - 验证 marketplace 功能

---

## 目录结构

```
example-marketplace/
├── .claude-plugin/
│   └── marketplace.json    # Marketplace 配置文件
└── README.md               # 本文件
```

---

## 使用方法

### 方式 1：直接使用本示例

如果你想测试这个 marketplace：

```bash
# 1. 克隆 lsearch 仓库
git clone https://github.com/moringchen/lsearch.git
cd lsearch/example-marketplace

# 2. 添加本地 marketplace（开发测试）
npx skills add-marketplace file://$(pwd)

# 3. 搜索并安装 lsearch
npx skills find lsearch
npx skills add lsearch -g
```

### 方式 2：创建自己的 Marketplace

1. **Fork 或复制本目录**

2. **修改 `marketplace.json`**：
   - 更改 `name` - 你的 marketplace 名称
   - 更改 `author` - 作者信息
   - 可以添加更多 skills

3. **推送到 GitHub**

4. **分享给团队成员**：

```bash
# 添加你的 marketplace
npx skills add-marketplace https://github.com/your-org/your-marketplace

# 现在可以搜索了
npx skills find lsearch
```

---

## Marketplace.json 字段说明

| 字段 | 说明 |
|------|------|
| `name` | Marketplace 唯一名称 |
| `version` | Marketplace 版本 |
| `description` | 描述 |
| `author` | 作者信息 |
| `skills` | Skill 列表 |

### Skill 字段

| 字段 | 说明 |
|------|------|
| `name` | Skill 名称（唯一） |
| `description` | Skill 描述 |
| `source` | 代码源（github/pip/npm 等） |
| `entry.skill` | SKILL.md 文件路径 |
| `entry.commands` | 斜杠命令目录 |
| `entry.mcp` | MCP 服务器配置 |

---

## 高级用法：多 Skill Marketplace

你可以在一个 marketplace 中包含多个 skills：

```json
{
  "name": "my-team-skills",
  "skills": [
    {
      "name": "lsearch",
      "source": { "source": "github", "repo": "moringchen/lsearch" }
    },
    {
      "name": "my-internal-tool",
      "source": { "source": "github", "repo": "my-org/internal-tool" }
    }
  ]
}
```

---

## 常见问题

**Q: 为什么要用自定义 marketplace？**
A: 适合企业内部使用，或者 skills.sh 还没收录某个 skill 时。

**Q: 和直接 `npx skills add repo` 有什么区别？**
A: 通过 marketplace 可以让用户先搜索、了解后再安装，体验更好。

**Q: 可以商业使用吗？**
A: 可以，这是完全开源的示例。

**Q: lsearch 会出现在 skills.sh 排行榜吗？**
A: 会的！根据 skills.sh FAQ，当用户运行 `npx skills add moringchen/lsearch` 安装时，你的 skill 会自动通过匿名遥测数据出现在排行榜上，无需手动提交。

**Q: 为什么搜索不到 lsearch？**
A: skills.sh 的搜索功能可能只显示已安装量达到一定数量的 skills。你可以直接安装使用：`npx skills add moringchen/lsearch -g`

---

## 相关链接

- lsearch 仓库：https://github.com/moringchen/lsearch
- skills.sh：https://skills.sh
- MCP 协议：https://modelcontextprotocol.io/
