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

### Quick Start (Recommended)

You can run the server directly using `uvx` (part of the [uv](https://github.com/astral-sh/uv) toolkit):

```bash
uvx moomoo-api-mcp
```

### Permanent Installation

To install it as a persistent tool available in your shell:

```bash
uv tool install moomoo-api-mcp
# Then run:
moomoo-api-mcp
```

> **Note**: The `moomoo-api` Python SDK and other dependencies will be installed automatically.

### Development Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Litash/moomoo-api-mcp.git
   cd moomoo-api-mcp
   ```

2. **Install dependencies**:

   ```bash
   uv sync
   ```

3. **Run locally**:
   ```bash
   uv run moomoo-api-mcp
   ```

---

## Configuration

### 1. Prerequisites

#### Moomoo OpenD (Required)

The MCP server communicates with the Moomoo API via **Moomoo OpenD**, a local gateway application. You **MUST** install and run this first.

1. **Download OpenD**:
   - Visit the [Moomoo Open API Download Page](https://www.moomoo.com/download/opend).
   - Download the version appropriate for your OS (Windows/Mac/Linux).

2. **Install & Run**:
   - Install the application.
   - Launch **Moomoo OpenD**.
   - Log in with your Moomoo account credentials.

3. **Configure**:
   - Ensure the listening port is set to `11111` (this is the default).
   - **Note**: The MCP server connects to `127.0.0.1:11111` by default.

### 2. Environment Variables

To enable **REAL account** access, you must securely provide your credentials.

| Variable                | Description                                | Example  |
| ----------------------- | ------------------------------------------ | -------- |
| `MOOMOO_TRADE_PASSWORD` | Your trading password (plain text)         | `123456` |
| `MOOMOO_SECURITY_FIRM`  | Your broker region (e.g., FUTUSG, FUTUINC) | `FUTUSG` |

> **Note**: Without these, the server runs in **SIMULATE-only mode** (paper trading).

### 3. Configure Claude Desktop

Add the server to your `claude_desktop_config.json`:

#### Option A: Using PyPI Package (Recommended)

```json
{
  "mcpServers": {
    "moomoo": {
      "command": "uvx",
      "args": ["moomoo-api-mcp"],
      "env": {
        "MOOMOO_TRADE_PASSWORD": "your_trading_password",
        "MOOMOO_SECURITY_FIRM": "FUTUSG"
      }
    }
  }
}
```

#### Option B: Local Development

```json
{
  "mcpServers": {
    "moomoo": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\moomoo-api-mcp",
        "run",
        "moomoo-api-mcp"
      ],
      "env": {
        "MOOMOO_TRADE_PASSWORD": "your_trading_password",
        "MOOMOO_SECURITY_FIRM": "FUTUSG"
      }
    }
  }
}
```

> **Security**: Never commit your password to version control. The `env` block in the config file remains local.

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
