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

### Environment Variables

To enable **REAL account** access, set your trading password via environment variable:

| Variable                    | Description                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| `MOOMOO_TRADE_PASSWORD`     | Your Moomoo trading password (plain text)                                                   |
| `MOOMOO_TRADE_PASSWORD_MD5` | MD5 hash of your trading password (alternative)                                             |
| `MOOMOO_SECURITY_FIRM`      | Securities firm: `FUTUSG` (Singapore), `FUTUSECURITIES` (HK), `FUTUINC` (US), `FUTUAU` (AU) |

> **Note**: If both password vars are set, `MOOMOO_TRADE_PASSWORD` takes precedence.

Without these variables, the server runs in **SIMULATE-only mode** (paper trading).

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
      ],
      "env": {
        "MOOMOO_TRADE_PASSWORD": "your_trading_password",
        "MOOMOO_SECURITY_FIRM": "FUTUSG"
      }
    }
  }
}
```

> **Security**: Never commit your password to git. The `env` block in the config file is local-only.

## AI Agent Guidance

> **IMPORTANT**: All account tools default to **REAL** trading accounts.

When using this MCP server, AI agents **MUST**:

1. **Notify the user clearly** before accessing REAL account data. Example:

   > "I'm about to access your **REAL trading account**. This will show your actual portfolio and balances."

2. **Follow the unlock workflow** for REAL accounts:
   - First call `unlock_trade(password='...')` with the user's trading password
   - Then call account tools (they default to `trd_env='REAL'`)

3. **Only use SIMULATE accounts when explicitly requested** by the user. To use simulation:
   - Pass `trd_env='SIMULATE'` parameter explicitly
   - No unlock is required for simulation accounts

### Workflow Example

```text
User: "Show me my portfolio"

Agent Response:
"I'm accessing your REAL trading account to show your portfolio.
If you prefer to use a simulation account instead, please let me know."

[Proceeds to unlock_trade → get_account_summary]
```

---

## Disclaimer

**Unofficial Project**: This software is an independent open-source project and is **not** affiliated with, endorsed by, or sponsored by Moomoo Inc., Futu Holdings Ltd., or their affiliates.

- **Use at your own risk**: Trading involves financial risk. The authors provide this software "as is" without warranty of any kind.
- **Test First**: Always test your agents and tools in the **Simulation (Paper Trading)** environment before using real funds.
