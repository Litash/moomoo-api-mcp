# Design: Account Information Tools

## Architecture

We will follow the existing service pattern used in `QuoteService` (documented in project.md).

### TradeService

`TradeService` will manage the `OpenSecTradeContext`.

```python
class TradeService(MoomooService):
    def __init__(self, host='127.0.0.1', port=11111):
        super().__init__(host, port)
        self.trade_ctx = None

    def connect(self):
        # Initialize OpenSecTradeContext
        pass

    def get_accounts(self) -> list[dict]:
        # Call get_acc_list
        pass

    def get_assets(self) -> dict:
        # Call accinfo_query
        pass

    def get_positions(self) -> list[dict]:
        # Call position_list_query
        pass

    def get_max_tradable(self, code: str, price: float) -> int:
        # Call acctradinginfo_query
        pass

    def get_margin_ratio(self) -> dict:
        # Call Trd_GetMarginRatio
        pass

    def get_cash_flow(self, start: str, end: str) -> list[dict]:
        # Call get_acc_cash_flow (API name guess, need to verify maps to "Get Cash Flow Summary")
        pass

    def unlock_trade(self, password: str) -> None:
        # Call unlock_trade
        pass
```

### Tools

New module `src/moomoo_mcp/tools/account.py`.

- `get_accounts`: Returns list of accounts.
- `get_assets`: Returns asset details (cash, market value) for the connected account.
- `get_positions`: Returns current positions.
- `get_max_tradable`: Returns maximum tradable quantity for a specific stock and price.
- `get_margin_ratio`: Returns margin ratios.
- `get_cash_flow`: Returns cash flow history.
- `unlock_trade`: Unlocks trading permissions (required for some queries and trading).

## Interfaces

The tools will return JSON-serializable dictionaries/lists as defined by `moomoo-api` response structures, converted to Python native types (e.g. converting pandas DataFrames to records).
