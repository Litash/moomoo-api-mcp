# Design: Market Data Tools

## Overview

We need to expose market data to the agent. We will create a `MarketDataService` that manages the `OpenQuoteContext`.

## Components

### `MarketDataService`

- Wrapper around `OpenQuoteContext`.
- Handles connection and subscription limits (if any).
- Methods:
  - `get_stock_quote(codes: List[str])`
  - `get_historical_kline(code: str, start: str, end: str, ktype: str)`
  - `get_market_snapshot(codes: List[str])`
  - `get_order_book(code: str)`

### Tools

- `get_stock_quote`: Returns list of quote details.
- `get_historical_kline`: Returns DF or list of kline data.
- `get_market_snapshot`: Returns snapshot data.
- `get_order_book`: Returns bid/ask queues.

## Considerations

- **Data Volume**: K-line data can be large. We should limit the default return size or paginate if possible. For the agent, returning the last N bars might be more useful than a full history dump unless requested.
- **Subscriptions**: Real-time data often requires "subscriptions" in Moomoo API. The `get_stock_quote` might implicitly handle subscription or we might need a separate `subscribe` tool. For simplicity, we will try to handle subscription automatically in the service if needed for the "snapshot" or "quote" call, or use the "Snapshot" API which typically doesn't require persistent subscription overhead for a single check.
  - _Correction_: snapshot usually requires valid quota but not necessarily a persistent streaming subscription. `get_market_snapshot` is efficient for batch. `get_stock_quote` usually implies real-time subscription. We will prioritize `snapshot` for batch and `quote` for single/detail.
