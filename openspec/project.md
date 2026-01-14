# Project Context

## Purpose

MCP (Model Context Protocol) server that enables AI agents (Gemini CLI, Claude Code, etc.) to interact with the Moomoo trading platform. Provides tools for market data retrieval, trading operations, and account management through the moomoo-api SDK.

## Tech Stack

- **Language**: Python 3.14
- **MCP SDK**: `mcp` (Model Context Protocol Python SDK) with FastMCP
- **Trading API**: `moomoo-api` (moomoo OpenAPI Python SDK)
- **Package Manager**: uv
- **Data Processing**: pandas

## Project Conventions

### Python 3.14 Code Style

#### Formatting & Linting

- **Formatter**: ruff format
- **Linter**: ruff check
- **Line length**: 88 characters (ruff default)
- **Import sorting**: ruff with isort rules

#### Type Annotations (PEP 649 - Deferred Evaluation)

Python 3.14 defers annotation evaluation - no need for `from __future__ import annotations` or string quotes for forward references.

```python
# Python 3.14 style - no quotes needed for forward references
def get_order(order_id: str) -> Order:  # Order can be defined later
    ...

class Order:
    next_order: Order | None = None  # Self-reference works directly
```

#### Type Hints Best Practices

- Required for all public functions and methods
- Use `|` union syntax: `str | None` (not `Optional[str]`)
- Use built-in generics: `list[str]`, `dict[str, int]` (not `List`, `Dict`)
- Use `collections.abc` for protocols: `Sequence`, `Mapping`, `Callable`

```python
# Preferred Python 3.14 style
def process_codes(codes: list[str]) -> dict[str, float]:
    ...

def fetch_data(callback: Callable[[str], None] | None = None) -> None:
    ...
```

#### Naming Conventions

- `snake_case`: functions, variables, module names
- `PascalCase`: classes, type aliases
- `SCREAMING_SNAKE_CASE`: constants
- `_private`: internal functions/variables (single underscore)

#### Docstrings

Google style for all public functions, tools, and resources:

```python
def get_market_snapshot(codes: list[str]) -> dict[str, MarketData]:
    """Get current market snapshot for specified stocks.

    Args:
        codes: List of stock codes (e.g., ['HK.00700', 'US.AAPL']).

    Returns:
        Dictionary mapping stock codes to their market data.

    Raises:
        ConnectionError: If OpenD gateway is not available.
    """
```

#### Template Strings (PEP 750 - t-strings)

Use t-strings for structured logging and safe string interpolation where appropriate:

```python
# For structured logging (when library support is available)
code = "HK.00700"
log_msg = t"Fetching quote for {code}"
```

### MCP Server Architecture

#### Project Structure

```
moomoo-trading-analyst/
├── pyproject.toml
├── src/
│   └── moomoo_mcp/
│       ├── __init__.py
│       ├── server.py          # FastMCP server definition
│       ├── tools/             # MCP tool implementations
│       │   ├── __init__.py
│       │   ├── quotes.py      # Quote-related tools
│       │   └── trading.py     # Trading-related tools
│       ├── resources/         # MCP resource definitions
│       │   └── __init__.py
│       ├── services/          # Moomoo API wrapper services
│       │   ├── __init__.py
│       │   ├── quote_service.py
│       │   └── trade_service.py
│       └── models.py          # Pydantic models / dataclasses
├── tests/
│   ├── conftest.py
│   ├── test_tools/
│   └── test_services/
└── openspec/
```

#### FastMCP Server Pattern

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from moomoo_mcp.services.quote_service import QuoteService
from moomoo_mcp.services.trade_service import TradeService


@dataclass
class AppContext:
    """Application context with typed dependencies."""
    quote_service: QuoteService
    trade_service: TradeService


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage moomoo connections lifecycle."""
    quote_service = QuoteService()
    trade_service = TradeService()

    await quote_service.connect()
    await trade_service.connect()

    try:
        yield AppContext(
            quote_service=quote_service,
            trade_service=trade_service,
        )
    finally:
        await quote_service.disconnect()
        await trade_service.disconnect()


mcp = FastMCP(
    "Moomoo Trading",
    lifespan=app_lifespan,
)
```

#### Tool Implementation Pattern

```python
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from moomoo_mcp.server import AppContext, mcp


@mcp.tool()
async def get_quote(
    code: str,
    ctx: Context[ServerSession, AppContext],
) -> dict[str, float]:
    """Get real-time quote for a stock.

    Args:
        code: Stock code (e.g., 'HK.00700', 'US.AAPL').

    Returns:
        Quote data including price, volume, and change.
    """
    await ctx.info(f"Fetching quote for {code}")

    quote_service = ctx.request_context.lifespan_context.quote_service
    result = await quote_service.get_snapshot(code)

    if result.error:
        await ctx.warning(f"Quote fetch failed: {result.error}")
        return {"error": result.error}

    return result.data
```

#### Resource Implementation Pattern

```python
@mcp.resource("account://info")
async def get_account_info(ctx: Context[ServerSession, AppContext]) -> str:
    """Expose current account information."""
    trade_service = ctx.request_context.lifespan_context.trade_service
    accounts = await trade_service.get_accounts()
    return json.dumps(accounts, indent=2)
```

#### Context Usage for Logging & Progress

```python
@mcp.tool()
async def place_order(
    code: str,
    side: str,
    qty: int,
    price: float,
    ctx: Context[ServerSession, AppContext],
) -> dict:
    """Place a trading order."""
    # Structured logging
    await ctx.info(f"Placing {side} order: {qty} shares of {code} @ {price}")
    await ctx.debug(f"Order details: code={code}, side={side}, qty={qty}, price={price}")

    # Progress reporting for long operations
    await ctx.report_progress(progress=0.0, total=1.0, message="Validating order...")
    # ... validation logic ...

    await ctx.report_progress(progress=0.5, total=1.0, message="Submitting order...")
    # ... submission logic ...

    await ctx.report_progress(progress=1.0, total=1.0, message="Order placed")

    return {"order_id": order_id, "status": "submitted"}
```

#### Error Handling Pattern

```python
from mcp.shared.exceptions import McpError


@mcp.tool()
async def get_positions(ctx: Context[ServerSession, AppContext]) -> list[dict]:
    """Get current positions."""
    try:
        trade_service = ctx.request_context.lifespan_context.trade_service
        positions = await trade_service.get_positions()
        return positions
    except ConnectionError as e:
        await ctx.error(f"OpenD connection failed: {e}")
        return [{"error": "OpenD gateway not available"}]
    except Exception as e:
        await ctx.error(f"Unexpected error: {e}")
        raise
```

### Testing Strategy

- **Framework**: pytest with pytest-asyncio
- **Mocking**: Use `unittest.mock` for moomoo-api responses
- **Fixtures**: Shared fixtures in `conftest.py` for MCP server and mock services
- **Integration tests**: Require OpenD gateway running (marked with `@pytest.mark.integration`)

```python
import pytest
from mcp.server.fastmcp.testing import TestClient

from moomoo_mcp.server import mcp


@pytest.fixture
def client():
    return TestClient(mcp)


async def test_get_quote(client):
    result = await client.call_tool("get_quote", {"code": "HK.00700"})
    assert "price" in result
```

### Git Workflow

- **Main branch**: `main`
- **Feature branches**: `feature/<description>`
- **Commit messages**: Conventional commits (feat:, fix:, docs:, refactor:, test:, chore:)

## Domain Context

### Moomoo OpenAPI Architecture

- **OpenD**: Gateway program that must run locally or on cloud server. Handles TCP connections to Moomoo servers.
- **moomoo-api**: Python SDK that communicates with OpenD via TCP (default port 11111)
- **Authentication**: Requires moomoo ID login through OpenD

### Supported Markets

- **Hong Kong**: Stocks, ETFs, Warrants, CBBCs, Options, Futures
- **US**: Stocks, ETFs, Options, Futures (NYSE, NYSE-American, Nasdaq)
- **A-share (China)**: Stocks, ETFs via China Connect
- **Singapore/Japan**: Futures only

### Key Concepts

- **Quote API**: Real-time and historical market data (subscriptions, snapshots, candlesticks)
- **Trade API**: Order placement, modification, cancellation for live and paper trading
- **Paper Trading**: Simulated trading for testing strategies (TrdEnv.SIMULATE)

## Moomoo API Reference

### Core Classes

```python
from moomoo import *

# Quote context - for market data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# Trade context - for securities trading
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111)

# Always close contexts when done
quote_ctx.close()
trd_ctx.close()
```

### Quote API Methods

| Method                                           | Description                                     |
| ------------------------------------------------ | ----------------------------------------------- |
| `get_market_snapshot(codes)`                     | Get current market snapshot for stocks          |
| `get_stock_basicinfo(market, sec_type, codes)`   | Get basic stock information                     |
| `subscribe(codes, sub_types)`                    | Subscribe to real-time data                     |
| `request_history_kline(code, start, end, ktype)` | Get historical candlestick data                 |
| `get_rt_data(code)`                              | Get real-time tick data (requires subscription) |

### Trade API Methods

| Method                                             | Description                   |
| -------------------------------------------------- | ----------------------------- |
| `get_acc_list()`                                   | Get list of trading accounts  |
| `unlock_trade(password)`                           | Unlock trade for live trading |
| `place_order(price, qty, code, trd_side, trd_env)` | Place an order                |
| `modify_order(op, order_id, qty, price, trd_env)`  | Modify or cancel order        |
| `order_list_query(trd_env)`                        | Get open orders               |
| `history_order_list_query(trd_env)`                | Get order history             |

### Key Enums

```python
# Trading environment
TrdEnv.REAL      # Live trading
TrdEnv.SIMULATE  # Paper trading

# Order side
TrdSide.BUY
TrdSide.SELL

# Markets
TrdMarket.HK     # Hong Kong
TrdMarket.US     # United States
TrdMarket.CN     # China A-shares

# Subscription types
SubType.QUOTE       # Real-time quotes
SubType.ORDER_BOOK  # Order book depth
SubType.RT_DATA     # Tick-by-tick data
SubType.K_1M        # 1-minute candlesticks

# Candlestick types
KLType.K_1M    # 1 minute
KLType.K_5M    # 5 minutes
KLType.K_15M   # 15 minutes
KLType.K_60M   # 60 minutes
KLType.K_DAY   # Daily
KLType.K_WEEK  # Weekly

# Order operations
ModifyOrderOp.CANCEL  # Cancel order
ModifyOrderOp.MODIFY  # Modify order

# Market types
Market.HK, Market.US, Market.SH, Market.SZ

# Security types
SecurityType.STOCK, SecurityType.ETF, SecurityType.WARRANT
```

### Stock Code Format

- Hong Kong: `HK.00700` (Tencent), `HK.09988` (Alibaba HK)
- US: `US.AAPL` (Apple), `US.TSLA` (Tesla)
- Shanghai: `SH.600519` (Moutai)
- Shenzhen: `SZ.000001` (Ping An)

### Return Pattern

All moomoo API methods return a tuple: `(ret_code, data)`

```python
ret, data = quote_ctx.get_market_snapshot(['HK.00700'])
if ret == RET_OK:
    print(data)  # pandas DataFrame
else:
    print('Error:', data)  # error message string
```

## Important Constraints

- **OpenD Required**: MCP server cannot function without OpenD gateway running
- **Market Data Subscriptions**: Limited concurrent subscriptions based on account tier
- **Rate Limits**: Be mindful of API request frequency
- **Trading Hours**: Order operations subject to market hours
- **No Secrets in Code**: API credentials, user IDs, and account numbers must NEVER be in code or git history. Use environment variables or OpenD config.

## External Dependencies

### Required Services

- **OpenD Gateway**: Must be installed and running (Windows, macOS, Linux supported)
  - Download: https://www.moomoo.com/download/OpenAPI
  - Default TCP port: 11111
- **Moomoo Account**: Required for authentication and market data access

### Python Packages

```toml
# pyproject.toml dependencies
[project]
requires-python = ">=3.14"
dependencies = [
    "mcp>=1.0.0",           # Model Context Protocol SDK
    "moomoo-api>=9.0.0",    # Moomoo trading API SDK
    "pandas>=2.0.0",        # Data manipulation
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.4.0",
]

[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]

[tool.ruff.lint.isort]
known-first-party = ["moomoo_mcp"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```
