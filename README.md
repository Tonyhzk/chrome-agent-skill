<div align="center">

![Browser Chrome Agent](assets/banner.png)

A Claude Code Skill for browser automation via WebSocket communication with the Chrome extension, enabling web navigation, interaction, screenshots, and page snapshots.

**English** | [中文](README_CN.md) | [Changelog](CHANGELOG.md)

</div>

---

## Features

### Core Capabilities
- **Page Navigation** - Navigate to URLs, go back/forward
- **Element Interaction** - Click, hover, type text, select options, drag elements
- **Screenshots** - Capture visible page as PNG (save to file or return base64)
- **Page Snapshots** - Get ARIA accessibility tree for structured page analysis
- **Keyboard Input** - Press any key, submit forms
- **Page Source** - Get full HTML source code and save to file
- **Console Logs** - Retrieve browser console output

### Architecture

![Architecture](assets/architecture.png)

The server communicates with the Browser MCP Chrome extension over WebSocket. Commands are sent as JSON via stdin, and results are returned via stdout.

### Additional Tools
- **Batch URL Resolver** - Resolve redirect URLs in bulk via HTTP requests (no browser required)

---

## System Requirements

| Requirement | Details |
|-------------|---------|
| Python | 3.8+ |
| Chrome | With Browser MCP extension installed |
| OS | Windows / macOS / Linux |
| [persistent-shell-skill](https://github.com/Tonyhzk/persistent-shell-skill) | Recommended for Claude Code to keep the server running |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Tonyhzk/chrome-agent-skill.git
```

### 2. Install the Chrome Extension

1. Open `chrome://extensions/` in Chrome
2. Enable **Developer mode**
3. Drag the `.crx` file from `src/browser-chrome-agent/assets/` into the page to install; or unzip `Browser_MCP_1_3_4_modified.zip` and use "Load unpacked" (modified version with page source support)
4. Pin the Browser MCP extension for easy access

### 3. Install Python Dependencies

```bash
pip3 install websockets
```

### 4. Set Up Shared Configuration (Optional)

If you use a shared `.claude` configuration across projects:

```bash
python3 setup_claude_dir.py
```

This creates a symlink from the project's `.claude` directory to your shared configuration.

---

## Quick Start

### 1. Start the WebSocket Server

```bash
python3 src/browser-chrome-agent/scripts/server.py --port 9009
```

### 2. Connect the Extension

Click the Browser MCP extension icon in Chrome and click **Connect**.

### 3. Send Commands

Send JSON commands via stdin (one per line):

```json
{"action": "navigate", "params": {"url": "https://example.com"}}
{"action": "snapshot", "params": {}}
{"action": "click", "params": {"ref": "s1e5"}}
{"action": "screenshot", "params": {"savePath": "./screenshot.png"}}
```

---

## Available Actions

| Action | Params | Description |
|--------|--------|-------------|
| `navigate` | `{"url": "..."}` | Navigate to URL |
| `go_back` | `{}` | Go back |
| `go_forward` | `{}` | Go forward |
| `click` | `{"ref": "s1e5"}` | Click element |
| `hover` | `{"ref": "s1e5"}` | Hover over element |
| `type` | `{"ref": "s1e5", "text": "...", "submit": false}` | Type text |
| `select_option` | `{"ref": "s1e5", "values": ["..."]}` | Select dropdown option |
| `drag` | `{"startRef": "s1e5", "endRef": "s1e8"}` | Drag element |
| `press_key` | `{"key": "Enter"}` | Press key |
| `wait` | `{"time": 2}` | Wait (seconds) |
| `screenshot` | `{}` or `{"savePath": "path"}` | Capture screenshot |
| `snapshot` | `{}` | Get ARIA page snapshot |
| `get_html` | `{"savePath": "path"}` | Get full page HTML source and save to file |
| `get_console_logs` | `{}` | Get console logs |
| `status` | - | Check connection status |
| `quit` | - | Shut down server |

### Element References

Interactive actions (`click`, `hover`, `type`, etc.) use `ref` values from the ARIA snapshot. Run `snapshot` first to get the page structure, then use the `[ref=xxx]` values to target elements.

---

## Project Structure

```
chrome-agent-skill/
├── src/browser-chrome-agent/
│   ├── SKILL.md              # Skill definition
│   ├── scripts/
│   │   ├── server.py         # WebSocket server (main entry)
│   │   ├── context.py        # WebSocket connection manager
│   │   ├── tools.py          # Browser automation tools
│   │   ├── utils.py          # Utility functions
│   │   ├── batch_resolve_urls.py  # Batch URL resolver
│   │   └── requirements.txt  # Python dependencies
│   └── assets/               # Chrome extension packages
├── 0_Doc/                    # Documentation
├── 0_Design/                 # Design resources
├── setup_claude_dir.py       # Shared config symlink tool
├── CHANGELOG.md              # English changelog
└── CHANGELOG_CN.md           # Chinese changelog
```

---

## Acknowledgements

This project is a Python rewrite of [Browser MCP](https://github.com/BrowserMCP/mcp) (originally TypeScript/Node.js), adapted as a Claude Code Skill with a WebSocket-based stdin/stdout control interface.

- [Browser MCP](https://browsermcp.io/) - The original project and Chrome extension that powers browser automation

## License

[Apache License 2.0](LICENSE)

## Author

**Tonyhzk**

- GitHub: [@Tonyhzk](https://github.com/Tonyhzk)
- Email: 1125258615@qq.com