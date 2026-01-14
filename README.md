# Moomoo API MCP Server

An MCP (Model Context Protocol) server for the Moomoo trading platform. This server allows AI agents (like Claude Desktop or Gemini) to access market data, account information, and execute trades via the moomoo-api Python SDK.

## Features

- **System Health**: Check connectivity to OpenD gateway (`check_health`).
- **Exensible Architecture**: Built on FastMCP for easy extension of trading capabilities.

## Installation

### Prerequisites

- [Python 3.14+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) package manager
- [Moomoo OpenD](https://www.moomoo.com/download/OpenAPI) gateway installed and running

### Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd moomoo-api-mcp
   ```

2. **Install dependencies**:

   ```bash
   uv sync
   ```

3. **Configure OpenD**:
   - Launch OpenD and log in with your Moomoo account.
   - Ensure the gateway is listening on `127.0.0.1:11111` (default).

## Usage

### Run Locally

Start the MCP server:

```bash
uv run moomoo-mcp
```

### Configure Claude Desktop

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "moomoo": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\moomoo-api-mcp",
        "run",
        "moomoo-mcp"
      ]
    }
  }
}
```

## Disclaimer

**Unofficial Project**: This software is an independent open-source project and is **not** affiliated with, endorsed by, or sponsored by Moomoo Inc., Futu Holdings Ltd., or their affiliates.

- **Use at your own risk**: Trading involves financial risk. The authors provide this software "as is" without warranty of any kind.
- **Test First**: Always test your agents and tools in the **Simulation (Paper Trading)** environment before using real funds.
