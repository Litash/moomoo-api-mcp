# Spec: Market Snapshot

## ADDED Requirements

### Requirement: Retrieve Market Snapshots

The system MUST provide a tool `get_market_snapshot` that returns a snapshot of market data for a list of securities. This is often more efficient for getting "current status" of multiple stocks than opening subscriptions for all.

#### Scenario: User checks a watchlist

- **Given** power user has a watchlist of 10 stocks
- **When** the `get_market_snapshot` tool is called with the list of codes
- **Then** the system returns the latest price, change status, and volume for all 10 stocks.
