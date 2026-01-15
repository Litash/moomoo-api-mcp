# Proposal: Add Market Data Tools

## Goal

Enable the AI Agent to perform market analysis by providing access to market data and signals via the Moomoo API.

## Capabilities

- `market-quotes`: Retrieve real-time stock quotes.
- `market-kline`: Retrieve historical and real-time candlestick (K-line) data.
- `market-snapshot`: specific market snapshots for efficient batch data retrieval.
- `market-depth`: Access order book data (market depth).

## Why

To support quantitative trading analysis, an agent needs access to Price, Volume, and Order Depth data. The Moomoo API provides `OpenQuoteContext` for this purpose. This change adds tools to expose these capabilities.
