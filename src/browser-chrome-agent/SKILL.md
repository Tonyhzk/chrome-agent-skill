---
name: browser-chrome-agent
version: 1.4.0
description: 浏览器自动化控制技能。通过 WebSocket 连接 Chrome 扩展，实现网页导航、点击、输入、截图、获取页面快照、多标签页管理等操作。当用户需要操作浏览器、自动化网页交互、截取网页截图、获取页面内容、切换标签页时使用。关键词：浏览器、Chrome、网页操作、自动化、截图、点击、导航、输入、页面快照、标签页、多标签。
---

# Browser Chrome Agent

通过 WebSocket 与 Chrome 扩展通信，控制用户浏览器执行自动化操作。

## 前置条件

1. Chrome 浏览器已安装 Browser MCP 扩展
   - **本技能默认分发修改版插件**：`assets/` 目录内仅包含修改版插件，支持所有文档中列出的功能（包括 `get_html`、`snapshot_file` 等增强功能）
   - 扩展安装包位于 `%当前SKILL文件父目录%/assets/` 目录
   - 安装方式：Chrome 地址栏输入 `chrome://extensions/`，开启「开发者模式」，解压 `Browser_MCP_1_3_4_modified.zip` 后通过「加载已解压的扩展程序」安装
2. 扩展已点击 Connect 建立连接
3. 推荐安装 [persistent-shell-skill](https://github.com/Tonyhzk/persistent-shell-skill) — 持久终端会话技能，用于在 Claude Code 中保持服务器持续运行

## 启动服务器

服务器需要持续运行并通过 stdin 接收 JSON 命令。

### 方式一：持久化终端技能（Claude Code 推荐）

需要 持久化终端 技能：

1. 创建名为 `browser-ws` 的后台会话
2. 在会话中执行：`python3 %当前SKILL文件父目录%/scripts/server.py --port 9009`
3. 等待几秒后读取输出，确认服务器启动和扩展连接

### 方式二：手动终端运行

没有持久化终端技能时，让用户在终端中手动直接运行：

```bash
python3 %当前SKILL文件父目录%/scripts/server.py --port 9009
```

启动后在同一终端中逐行输入 JSON 命令即可。

服务器启动后输出 `[server] WebSocket 服务器已启动`，扩展连接后输出 `[server] Chrome 扩展已连接`。

## 发送命令

逐行输入 JSON 命令：

```json
{"action": "navigate", "params": {"url": "https://example.com"}}
```

如果使用持久化终端，向 `browser-ws` 会话发送命令后等待 5-10 秒读取结果。

## 可用操作

| action | params | 说明 |
|--------|--------|------|
| `navigate` | `{"url": "..."}` | 导航到 URL |
| `go_back` | `{}` | 后退 |
| `go_forward` | `{}` | 前进 |
| `click` | `{"ref": "s1e5"}` 或 `{"x": 500, "y": 100}` | 点击元素（支持 ref 或坐标） |
| `hover` | `{"ref": "s1e5"}` | 悬停元素 |
| `type` | `{"ref": "s1e5", "text": "...", "submit": false}` | 输入文本 |
| `select_option` | `{"ref": "s1e5", "values": ["..."]}` | 选择下拉选项 |
| `drag` | `{"startRef": "s1e5", "endRef": "s1e8"}` | 拖拽 |
| `press_key` | `{"key": "Enter"}` | 按键 |
| `get_coordinates` | `{"ref": "s1e5"}` | 获取元素坐标位置 |
| `find_element` | `{"keyword": "搜索"}` | 通过关键字搜索元素，返回匹配的 ref 列表 |
| `find_and_locate` | `{"keyword": "搜索", "index": 0}` | 搜索元素并立即获取坐标（解决 ref 过期问题） |
| `get_text` | `{}` 或 `{"max_length": 5000}` | 获取页面纯文字内容 |
| `wait` | `{"time": 2}` | 等待（秒） |
| `screenshot` | `{}` 或 `{"savePath": "全路径"}` | 截图，传 savePath（必须是全路径）保存到文件，不传返回 base64 |
| `snapshot` | `{}` | 获取页面 ARIA 快照 |
| `get_html` | `{"savePath": "全路径"}` | 获取页面完整 HTML 源码并保存到文件（savePath 必须是全路径，仅修改版插件可用） |
| `get_console_logs` | `{}` | 获取控制台日志 |
| `list_tabs` | `{}` | 列出所有标签页（显示 id、标题、URL，`*` 标记活动页） |
| `new_tab` | `{"url": "..."}` | 打开新标签页（url 可选，默认 about:blank） |
| `switch_tab` | `{"tabId": 123456}` | 切换到指定标签页（tabId 从 list_tabs 获取） |
| `close_tab` | `{"tabId": 123456}` | 关闭指定标签页 |
| `status` | - | 查询连接状态 |
| `quit` | - | 关闭服务器 |

## 响应格式

```json
{"success": true, "data": {"type": "text", "text": "..."}}
{"success": false, "error": "错误信息"}
```

## ref 参数说明

交互操作（click/hover/type/select_option/drag）使用 ARIA 快照中的 `ref` 值定位元素。先用 `snapshot` 获取页面结构，再使用快照中的 `[ref=xxx]` 值操作元素。

## 操作规范

### snapshot_file 参数（按需使用）

所有会返回快照的操作（navigate/click/type/hover/select_option/drag/snapshot/switch_tab）都支持 `snapshot_file` 参数。

**默认不传 `snapshot_file`**，操作只返回 URL + Title，不获取也不输出快照。仅在需要查看页面结构时传入 `snapshot_file`，快照写入文件，stdout 仍只返回 URL + Title + 文件路径。**快照内容禁止直接输出到上下文**。

使用时将快照保存到固定文件（**必须使用全路径**，如 `/Users/xxx/project/.temp/browser/snapshot.txt`），需要查看时用 Read 工具读取。缓存目录存在时无需重复创建。

```json
{"action": "click", "params": {"ref": "s1e5", "snapshot_file": "/Users/xxx/project/.temp/browser/snapshot.txt"}}
```

### 查找指令优先，禁止先 snapshot

**核心原则：直接使用查找指令定位元素，禁止先获取 snapshot 再手动查找**

- **优先使用 `find_element` 或 `find_and_locate`**：通过关键词直接搜索元素，返回匹配的 ref 列表或坐标
  - `find_element`：返回所有匹配元素的 ref 列表，适合需要选择特定元素的场景
  - `find_and_locate`：搜索并立即返回指定索引元素的坐标，一步到位，避免 ref 过期
- **禁止先 snapshot 再手动查找**：这会浪费时间和上下文空间，且容易遇到 ref 过期问题
- **snapshot 仅用于调试**：当查找指令无法定位元素，或需要了解页面整体结构时才使用
- **交互操作默认只返回 URL+Title**：click/type 等操作不输出快照，需要查看页面结构时传 `snapshot_file`
- `screenshot` 仅在以下场景使用：
  - 需要视觉确认（验证排版效果、图片显示、样式问题）
  - 用户明确要求截图
  - 调试时查找指令和快照信息都不足以判断页面状态

**正确流程示例**：
```json
// ✅ 正确：直接使用查找指令
{"action": "find_element", "params": {"keyword": "登录按钮"}}
// 返回 ["s1e5", "s1e12"]，选择合适的 ref 进行操作

// ✅ 正确：一步到位获取坐标
{"action": "find_and_locate", "params": {"keyword": "搜索框", "index": 0}}
// 直接返回坐标，避免 ref 过期

// ❌ 错误：先 snapshot 再手动查找
{"action": "snapshot", "params": {"snapshot_file": "/path/to/snapshot.txt"}}
// 然后读取文件手动查找 ref - 这是禁止的！
```

### ref 过期处理

- 每次交互操作后页面 DOM 可能更新，ref 前缀会递增（s1e → s2e → s3e）
- 操作返回的快照中包含最新 ref，后续操作必须使用最新 ref
- 遇到 `Stale aria-ref` 错误时，读取快照文件获取新 ref 重试即可

### 禁止使用 read 命令

- 持久化终端的 `read` 命令会返回整个会话历史，严重占用上下文
- **非调试情况下禁止使用 `read`**，只用 `exec` 执行命令并获取单条结果

### 快照文件读取规范

- **优先使用查找指令**：需要定位元素时，直接使用 `find_element` 或 `find_and_locate`，不要读取快照文件手动查找
- **快照文件仅用于调试**：当查找指令无法定位元素，需要了解页面结构时才读取快照文件
- **禁止整个读取快照文件**：快照通常有数百到上千行，会严重占用上下文
- 需要查看快照时，使用 Grep 搜索关键词（如按钮文字、输入框名称）
- 需要上下文时，用 Read 的 `offset` + `limit` 参数读取指定行范围

### 多标签页操作规范

- **开始操作前先确认当前标签页**：使用 `list_tabs` 查看所有标签页，确认要操作的是哪个标签页
- 活动标签页会用 `*` 标记，所有操作都作用于当前活动标签页
- `new_tab` 创建后会自动切换到新标签页（包括 debugger attach），可直接操作
- `close_tab` 关闭当前活动标签页后会自动切换到下一个活动标签页
- 如需操作其他已有标签页，用 `switch_tab` 切换（切换后会返回目标页面快照）
- `switch_tab` 会完成 debugger 的 detach/attach，确保键盘鼠标事件发送到正确的标签页

### type 输入规范

- `type` 操作是**追加输入**，不会清空输入框原有内容
- 如果输入框已有内容需要替换：先点击输入框聚焦，再输入新内容（从空输入框开始最可靠）
- 或者导航到目标页面的初始状态（如首页），确保输入框为空再操作

## 批量解析跳转链接

独立脚本，不依赖浏览器，通过 HTTP 请求批量解析跳转页面中的真实目标 URL。

脚本路径：`%当前SKILL文件父目录%/scripts/batch_resolve_urls.py`

### 使用方式

```bash
# 方式一：JSON 配置文件
python3 %当前SKILL文件父目录%/scripts/batch_resolve_urls.py --config config.json

# 方式二：文本文件（每行: 名称 | URL）
python3 %当前SKILL文件父目录%/scripts/batch_resolve_urls.py --urls urls.txt --output result.md --title "标题"
```

### 配置文件格式

```json
{
    "links": [
        {"name": "网站名", "url": "https://example.com/jump/site"}
    ],
    "output": "output.md",
    "extract_patterns": ["goToLink\\(\\d+,\\s*'(https?://[^']+)'"],
    "delay": 0.3,
    "title": "文档标题",
    "description": "来源说明"
}
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--config` | JSON 配置文件路径 |
| `--urls` | URL 列表文件（每行: `名称 \| URL`） |
| `--output` | 输出 Markdown 文件路径（默认 output.md） |
| `--delay` | 请求间隔秒数（默认 0.3） |
| `--title` | 文档标题 |
| `--description` | 文档描述 |

默认内置 `goToLink()`、`window.location`、`meta refresh`、`data-url` 等常见前端跳转提取模式，可通过配置文件的 `extract_patterns` 自定义。

## 关闭服务器

发送 quit 命令：`{"action": "quit"}`

或直接 `Ctrl+C` 终止进程。

## 项目信息

- 作者：[Tonyhzk](https://github.com/Tonyhzk)
- 官方仓库：[chrome-agent-skill](https://github.com/Tonyhzk/chrome-agent-skill)
- 原始仓库：[BrowserMCP/mcp](https://github.com/BrowserMCP/mcp)
- 原始网站：[browsermcp.io](https://browsermcp.io/)
