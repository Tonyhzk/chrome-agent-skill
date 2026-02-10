---
name: browser-chrome-agent
version: 1.1.0
description: 浏览器自动化控制技能。通过 WebSocket 连接 Chrome 扩展，实现网页导航、点击、输入、截图、获取页面快照等操作。当用户需要操作浏览器、自动化网页交互、截取网页截图、获取页面内容时使用。关键词：浏览器、Chrome、网页操作、自动化、截图、点击、导航、输入、页面快照。
---

# Browser Chrome Agent

通过 WebSocket 与 Chrome 扩展通信，控制用户浏览器执行自动化操作。

## 前置条件

1. Chrome 浏览器已安装 Browser MCP 扩展
   - 扩展安装包位于 `%当前SKILL文件父目录%/assets/` 目录
   - 安装方式：Chrome 地址栏输入 `chrome://extensions/`，开启「开发者模式」，将 `.crx` 文件拖入页面安装
   - 也可使用 `%当前SKILL文件父目录%/assets/Browser_MCP_1_3_4_modified.zip`，解压后通过「加载已解压的扩展程序」安装（此为修改版，支持 `get_html` 获取页面源码）
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
| `click` | `{"ref": "s1e5"}` | 点击元素 |
| `hover` | `{"ref": "s1e5"}` | 悬停元素 |
| `type` | `{"ref": "s1e5", "text": "...", "submit": false}` | 输入文本 |
| `select_option` | `{"ref": "s1e5", "values": ["..."]}` | 选择下拉选项 |
| `drag` | `{"startRef": "s1e5", "endRef": "s1e8"}` | 拖拽 |
| `press_key` | `{"key": "Enter"}` | 按键 |
| `wait` | `{"time": 2}` | 等待（秒） |
| `screenshot` | `{}` 或 `{"savePath": "路径"}` | 截图，传 savePath 保存到文件，不传返回 base64 |
| `snapshot` | `{}` | 获取页面 ARIA 快照 |
| `get_html` | `{"savePath": "路径"}` | 获取页面完整 HTML 源码并保存到文件（仅修改版插件可用） |
| `get_console_logs` | `{}` | 获取控制台日志 |
| `status` | - | 查询连接状态 |
| `quit` | - | 关闭服务器 |

## 响应格式

```json
{"success": true, "data": {"type": "text", "text": "..."}}
{"success": false, "error": "错误信息"}
```

## ref 参数说明

交互操作（click/hover/type/select_option/drag）使用 ARIA 快照中的 `ref` 值定位元素。先用 `snapshot` 获取页面结构，再使用快照中的 `[ref=xxx]` 值操作元素。

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
