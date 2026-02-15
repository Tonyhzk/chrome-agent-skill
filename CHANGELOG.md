# Changelog

All notable changes to this project will be documented in this file.

**English** | [中文](CHANGELOG_CN.md)

---

## [Unreleased]

### Added
- `snapshot_file` parameter for all snapshot-returning actions — snapshots are now only fetched and saved to file when explicitly requested, reducing context usage
- `switch_tab` now returns page info (URL + Title) after switching, confirming debugger attached correctly
- `close_tab` now reports which tab was auto-switched to after closing
- `list_tabs` now refreshes extension's internal active tab cache, fixing stale tabId issues after navigation
- `find_element` / `find_and_locate` promoted as primary element location method in SKILL.md

### Fixed
- Fixed multi-tab switching bug: keyboard/mouse events were sent to wrong tab after `switch_tab` due to JavaScript object reference issue in debugger tabId propagation
- Fixed `close_tab` not updating debugger attachment to new active tab when closing current tab

### Changed
- Default behavior: operations no longer output ARIA snapshots — only URL + Title returned by default, use `snapshot_file` to save snapshot to file when needed
- SKILL.md updated to enforce "find first, snapshot only for debug" workflow

## [1.2.0] - 2025-02-12

### Added
- `get_coordinates` action: get element coordinates
- `find_element` action: search page elements by keyword, return matching refs
- `find_and_locate` action: search element and get coordinates immediately (solves stale ref issue)
- `get_text` action: get page plain text content
- `list_tabs`, `new_tab`, `switch_tab`, `close_tab` actions: multi-tab management
- `click` action now supports coordinate clicking (`{"x": 500, "y": 100}`)
- Extracted modified Chrome extension source to `src/browser-mcp-crx/` for easier development
- Added `upstream/` directory to archive original Browser MCP extension and source

### Fixed
- Fixed `browser_get_coordinates` message listener not registered in Chrome extension
- Fixed persistent terminal exec unable to capture server output (termios echo interference)

### Changed
- Skill assets no longer include original extension or `.crx` files, unified to modified `.zip` package
- Server now supports persistent terminal marker protocol for direct exec result capture

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