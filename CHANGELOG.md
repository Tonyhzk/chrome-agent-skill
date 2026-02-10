# Changelog

All notable changes to this project will be documented in this file.

**English** | [中文](CHANGELOG_CN.md)

---

## [1.1.0] - 2025-02-11

### Added
- `get_html` action: retrieve full page HTML source and save to file
- Modified Chrome extension (Browser_MCP_1_3_4_modified) with `getPageHtml` message support
- Modified extension .zip source package for "Load unpacked" installation

### Fixed
- Fixed custom function name collision with original extension's React component in content script

## [1.0.0] - 2025-02-11

### Added
- WebSocket server with stdin JSON command interface for browser control
- Page navigation: `navigate`, `go_back`, `go_forward`
- Page interaction: `click`, `hover`, `type`, `select_option`, `drag`
- General actions: `press_key`, `wait`
- Information retrieval: `screenshot`, `snapshot`, `get_console_logs`
- Batch URL redirect resolver script `batch_resolve_urls.py`
- ARIA snapshot utility `utils.py`