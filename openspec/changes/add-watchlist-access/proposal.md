# Proposal: Add Watchlist Access Tools

## Why

The AI Agent currently lacks visibility into the user's watchlists and favorites in the Moomoo app. This limits its ability to analyze stocks that the user is interested in without explicit input of stock codes. Users have organized their portfolios and stocks of interest into watchlists (security groups) in the Moomoo app. The MCP server cannot currently access these lists, requiring users to manually provide stock codes for analysis.

## What Changes

Add two new tools to the `market-data` capability (managed via `market_data_service`):

1. `get_user_security_group`: Retrieves the list of custom security groups (watchlists).
2. `get_user_security`: Retrieves the list of stocks within a specific group.

These tools will wrap the existing `moomoo-api` methods `get_user_security_group` and `get_user_security`.

## Impact

- **Users**: Can ask the agent to "analyze my watchlist" or "show me quotes for my 'Tech' group".
- **Agent**: Gains context awareness of user's preferences and tracked assets.
