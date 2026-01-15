# Spec: Market Quotes

## ADDED Requirements

### Requirement: Retrieve Real-time Quotes

The system MUST provide a tool `get_stock_quote` that returns real-time quote data for a given list of stock codes.

#### Scenario: User requests quote for a stock

- **Given** the agent wants to know the current price of "US.AAPL"
- **When** the `get_stock_quote` tool is called with `codes=["US.AAPL"]`
- **Then** the system returns the current price, open, close, high, low, and volume for AAPL.
