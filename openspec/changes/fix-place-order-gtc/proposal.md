# Change: Fix Place Order Tool Limitation via Time in Force and Enhanced Order Types

## Why

The current `place_order` tool lacks support for specifying "Time in Force" (TIF) and limits the full range of order types available in the Moomoo API. Users need the ability to place GTC orders and utilize all supported order types (e.g., specialized market orders) to execute advanced trading strategies effectively.

## What Changes

- Add `time_in_force` parameter to `place_order` (Service & Tool).
- Ensure `place_order` tool supports and validates all `OrderType` enums:
  - NORMAL, MARKET, ABSOLUTE_LIMIT, AUCTION, AUCTION_LIMIT, SPECIAL_LIMIT
  - STOP, STOP_LIMIT, MARKET_IF_TOUCHED, LIMIT_IF_TOUCHED
  - TRAILING_STOP, TRAILING_STOP_LIMIT
  - TWAP, VWAP (if supported by environment)
- Validate compatibility between `time_in_force` and `order_type`.

## Impact

- Affected specs: `time-in-force-support` (modified), `order-type-support` (new).
- Affected code:
  - `src/moomoo_mcp/services/trade_service.py`
  - `src/moomoo_mcp/tools/trading.py`
