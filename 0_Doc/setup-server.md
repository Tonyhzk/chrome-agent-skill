# Set up MCP server

## Prerequisites

### Node.js

You need to have [Node.js](https://nodejs.org/en/download) installed to use the Browser MCP server.

## Add MCP server

Add the MCP server config to an AI application that supports MCP.
Example applications that support MCP:

Cursor

1. Open full Cursor settings
2. Navigate to the "Tools" tab
3. Click "New MCP server"
4. Add the server config below
5. Click the refresh button next to the "browsermcp" server to reload the server config

For more information, see [Cursor's MCP documentation](https://docs.cursor.com/context/model-context-protocol).

Claude Desktop

See [Claude's MCP documentation](https://modelcontextprotocol.io/quickstart/user)

Claude Desktop currently has a
[bug](https://github.com/modelcontextprotocol/servers/issues/812) where MCP
servers are started twice. This will cause Claude to show an error when using
the Browser MCP server but it will still work.

Windsurf

VS Code

### Server config

```
{
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["@browsermcp/mcp@latest"]
    }
  }
}
```
