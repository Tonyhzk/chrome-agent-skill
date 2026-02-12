# 更新日志

本项目的所有重要更改都将记录在此文件中。

[English](CHANGELOG.md) | **中文**

---

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