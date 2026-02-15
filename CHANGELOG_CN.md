# 更新日志

本项目的所有重要更改都将记录在此文件中。

[English](CHANGELOG.md) | **中文**

---

## [Unreleased]

### 新增
- `xpath_query` 操作：对页面 HTML 执行 XPath 查询，返回匹配元素的文本、内部/外部 HTML 或属性值（依赖 `lxml`）
- `snapshot` 操作新增 `inline` 参数：直接在响应中返回快照内容，无需保存到文件
- `snapshot` / `xpath_query` 新增 `max_length` 参数：控制返回内容截断长度，默认从 config.json 读取
- `xpath_query` 新增 `save_path` 参数：将完整查询结果保存到文件
- 支持通过 `config.json` 配置 `snapshot_max_length` 和 `xpath_max_display_length` 默认值

### 变更
- SKILL.md 新增"网页结构解析"工作流章节
- 更新 Chrome 扩展包（background.js 更新）

---

## [1.4.0] - 2026-02-15

### 新增
- 所有返回快照的操作支持 `snapshot_file` 参数 — 仅在明确请求时才获取快照并保存到文件，减少上下文占用
- `switch_tab` 切换后返回页面信息（URL + Title），确认 debugger 已正确 attach
- `close_tab` 关闭后报告自动切换到的标签页
- `list_tabs` 自动刷新扩展内部活动标签页缓存，修复导航后 tabId 过期问题
- `find_element` / `find_and_locate` 在 SKILL.md 中提升为首选元素定位方式

### 修复
- 修复多标签页切换 bug：`switch_tab` 后键盘/鼠标事件发送到错误标签页，根因是 JavaScript 对象引用问题导致 debugger tabId 未正确传播
- 修复 `close_tab` 关闭当前标签页后未将 debugger 附加到新活动标签页的问题

### 变更
- 默认行为变更：操作不再输出 ARIA 快照，默认只返回 URL + Title，需要快照时使用 `snapshot_file` 保存到文件
- SKILL.md 更新为"查找指令优先，snapshot 仅用于调试"的工作流

## [1.2.0] - 2025-02-12

### 新增
- `get_coordinates` 操作：获取元素坐标位置
- `find_element` 操作：通过关键字搜索页面元素，返回匹配的 ref 列表
- `find_and_locate` 操作：搜索元素并立即获取坐标（解决 ref 过期问题）
- `get_text` 操作：获取页面纯文字内容
- `list_tabs`、`new_tab`、`switch_tab`、`close_tab` 操作：多标签页管理
- `click` 操作支持坐标点击（`{"x": 500, "y": 100}`）
- 独立 Chrome 扩展修改版源码至 `src/browser-mcp-crx/`，便于开发维护
- 添加 `upstream/` 目录，存档原始 Browser MCP 扩展及源码

### 修复
- 修复 Chrome 扩展中 `browser_get_coordinates` 消息监听器未注册的问题
- 修复持久终端 exec 命令无法捕获服务器输出的问题（termios echo 干扰）

### 变更
- 技能 assets 中不再包含原版扩展和 `.crx` 文件，统一使用修改版 `.zip` 扩展包
- 服务器新增持久终端 marker 兼容，支持通过 exec 直接获取命令结果

## [1.1.0] - 2025-02-11

### 新增
- `get_html` 操作：获取页面完整 HTML 源码并保存到文件
- 修改版 Chrome 扩展（Browser_MCP_1_3_4_modified），支持 `getPageHtml` 消息
- 提供修改版扩展 .zip 源码包，支持「加载已解压的扩展程序」方式安装

### 修复
- 修复 content script 中自定义函数名与原始扩展 React 组件命名冲突的问题

## [1.0.0] - 2025-02-11

### 新增
- WebSocket 服务器，支持通过 stdin JSON 命令控制浏览器
- 页面导航：`navigate`、`go_back`、`go_forward`
- 页面交互：`click`、`hover`、`type`、`select_option`、`drag`
- 通用操作：`press_key`、`wait`
- 信息获取：`screenshot`、`snapshot`、`get_console_logs`
- 批量 URL 跳转解析脚本 `batch_resolve_urls.py`
- ARIA 快照辅助工具 `utils.py`