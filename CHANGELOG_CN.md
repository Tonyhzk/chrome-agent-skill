# 更新日志

本项目的所有重要更改都将记录在此文件中。

[English](CHANGELOG.md) | **中文**

---

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