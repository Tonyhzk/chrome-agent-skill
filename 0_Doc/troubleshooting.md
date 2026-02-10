# Troubleshooting

If you get an error, it is generally because of one of the following:

1. The MCP server is not running.
2. The browser is not connected to the MCP server.

## MCP server is not running

If the MCP server is not running, you will get errors when trying to run commands that use the MCP server.

Example (Cursor)

![Not connected error](https://mintcdn.com/browsermcp/e19Ahc63CA2bWPva/images/troubleshooting/not-connected-error.png?fit=max&auto=format&n=e19Ahc63CA2bWPva&q=85&s=9c9bbf9492defe44973ac0e7683a4251)

In order to run commands, the Browser MCP server must be running. View the list of MCP servers in your application to ensure that the Browser MCP server is running.

Disconnected server (Cursor)

![Disconnected server](https://mintcdn.com/browsermcp/e19Ahc63CA2bWPva/images/troubleshooting/disconnected-server.png?fit=max&auto=format&n=e19Ahc63CA2bWPva&q=85&s=fe462298c0fccdac2a3ee74dce5dac91)If the server is not running, ensure the server shows "Enabled" and click the refresh button to reload the server.



Connected server (Cursor)

![Connected server](https://mintcdn.com/browsermcp/e19Ahc63CA2bWPva/images/troubleshooting/connected-server.png?fit=max&auto=format&n=e19Ahc63CA2bWPva&q=85&s=722eadbf6c3930094b6d0269555e3c58)

### Client closed

If you see the message `Client closed` and clicking reload doesn't fix it, try removing `@latest` from the MCP server config so that you are using the package as `@browsermcp/mcp` instead of `@browsermcp/mcp@latest`.

## Browser is not connected to the MCP server

In order to connect the browser to the MCP server, install the Browser MCP extension and click the "Connect" button.
![Connect extension](https://mintcdn.com/browsermcp/e19Ahc63CA2bWPva/images/extension/connect-extension.png?fit=max&auto=format&n=e19Ahc63CA2bWPva&q=85&s=b1c78da850f219b0f913bf84c92aafbf)

## Other errors

If you encounter other errors, please file an issue on [GitHub](https://github.com/browsermcp/mcp/issues).
