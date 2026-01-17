# Moomoo API MCP Server

An MCP (Model Context Protocol) server for the Moomoo trading platform. This server allows AI agents (like Claude Desktop or Gemini) to access market data, account information, and execute trades via the moomoo-api Python SDK.

## Features

- **Market Data**: Real-time quotes, historical K-lines, market snapshots, and order books.
- **Account Management**: Comprehensive account summaries, assets, positions, and cash flow analysis.
- **Trading**: Full order management including placing, modifying, and canceling orders.
- **System Health**: Built-in health checks and connectivity verification.
- **Extensible Architecture**: Built on FastMCP for easy extension of trading capabilities.

## Tools

### System

- `check_health`: Check connectivity to Moomoo OpenD gateway and server health.

### Account

- `get_accounts`: List all trading accounts (REAL and SIMULATE).
- `get_account_summary`: Get a complete summary of assets and positions for an account.
- `get_assets`: Retrieve account assets (cash, market value, buying power).
- `get_positions`: Get current stock positions with P/L data.
- `get_max_tradable`: Calculate maximum tradable quantity for a specific stock.
- `get_margin_ratio`: Check margin ratios for specific stocks.
- `get_cash_flow`: Retrieve historical cash flow records.
- `unlock_trade`: Unlock trading access for REAL accounts.

### Market Data

- `get_stock_quote`: Get real-time stock quotes.
- `get_historical_klines`: Retrieve historical candlestick data (Day, Week, Min, etc.).
- `get_market_snapshot`: Get efficient market snapshots for multiple stocks.
- `get_order_book`: View real-time bid/ask order book depth.

### Trading

- `place_order`: Place a new order (Market, Limit, Stop, etc.).
- `modify_order`: Modify price or quantity of an open order.
- `cancel_order`: Cancel an open order.
- `get_orders`: Get list of orders for the current day.
- `get_deals`: Get list of executed trades (deals) for the current day.
- `get_history_orders`: Search historical orders.
- `get_history_deals`: Search historical deals.

## Installation

### Method 1: Quick Start with uvx (Recommended)

If you have `uv` installed, you can run the server directly without manual installation:

```bash
uvx moomoo-api-mcp
```

Or install it permanently as a tool:

```bash
uv tool install moomoo-api-mcp
```

### Method 2: Manual Setup (Development)

#### Prerequisites

- [Python 3.10+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) package manager
- [Moomoo OpenD](https://www.moomoo.com/download/OpenAPI) gateway installed and running

#### Steps

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

### Generating MD5 Password Hash

If you prefer not to store your plain text password in environment variables, you can generate an MD5 hash using PowerShell:

1. Open PowerShell
2. Run the following command (replace `your_trading_password` with your actual password):

   ```powershell
   $password = "your_trading_password"
   $md5 = [System.Security.Cryptography.HashAlgorithm]::Create("MD5")
   $utf8 = [System.Text.Encoding]::UTF8
   $hash = [System.BitConverter]::ToString($md5.ComputeHash($utf8.GetBytes($password))).Replace("-", "").ToLower()
   Write-Host "MD5 Hash: $hash"
   ```

3. Copy the output hash and set it as `MOOMOO_TRADE_PASSWORD_MD5`.

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
   - First call `unlock_trade` (it handles env vars automatically, or pass password if needed).
   - Then call account/trading tools (they default to `trd_env='REAL'`).

3. **Only use SIMULATE accounts when explicitly requested** by the user. To use simulation:
   - Pass `trd_env='SIMULATE'` parameter explicitly.
   - No unlock is required for simulation accounts.

### Workflow Example

```text
User: "Show me my portfolio"

Agent Response:
"I'm accessing your REAL trading account to show your portfolio.
If you prefer to use a simulation account instead, please let me know."

[Proceeds to unlock_trade → get_account_summary]
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

**Unofficial Project**: This software is an independent open-source project and is **not** affiliated with, endorsed by, or sponsored by Moomoo Inc., Futu Holdings Ltd., or their affiliates.

- **Use at your own risk**: Trading involves financial risk. The authors provide this software "as is" without warranty of any kind.
- **Test First**: Always test your agents and tools in the **Simulation (Paper Trading)** environment before using real funds.
