# Proposal: Add Account Information Tools

## Goal

Enable the AI agent to access trading account details, assets, positions, and trading capabilities.

## Rationale

To perform trading or analysis, the agent needs to understand the user's current portfolio state, purchasing power, and trading limits. The user specifically requested tools mapping to `accinfo_query`, `acctradinginfo_query`, `position_list_query`, `Trd_GetMarginRatio`, and `Get Cash Flow Summary`.
Additionally, `unlock_trade` is required for sensitive operations and trading preparation.

## Scope

- New `TradeService` in `src/moomoo_mcp/services/trade_service.py` wrapping `OpenSecTradeContext`.
- New tools in `src/moomoo_mcp/tools/account.py`:
  - `get_accounts` (Prerequisite)
  - `get_assets` (accinfo_query)
  - `get_positions` (position_list_query)
  - `get_max_tradable` (acctradinginfo_query)
  - `get_margin_ratio` (Trd_GetMarginRatio)
  - `get_cash_flow` (Get Cash Flow Summary)
  - `unlock_trade` (unlock_trade)
- Integration of `TradeService` into `server.py` lifespan.
- Unit tests for the new service and tools.
