# Changelog

Product updates

## May 7, 2025

v1.3.4

### 🛠 Fixed

* Fixed bug where console logs were cleared when another tab was opened or navigated
* Fixed bug where console logs were added multiple times when the tab was disconnected then re-connected

## April 14, 2025

v1.3.3

### 🛠 Fixed

* Allow automating on tabs that were opened before installing extension

## April 11, 2025

v1.3.2

### ✨ New

* Screenshot Tool
  + Browser MCP can now take a screenshot of the connected tab
  + In order to use the screenshot tool, reload the MCP server (e.g. click the reload button on Cursor) or restart your MCP client (e.g. close and reopen Claude Desktop) in order to load the latest MCP server version

### 🛠 Fixed

* Fixed bug where connection issues occur after closing a connected tab or connecting an invalid URL (e.g. new tab)
* Fixed bug where connection would fail when loading a page that includes 1Password or LastPass extension elements
