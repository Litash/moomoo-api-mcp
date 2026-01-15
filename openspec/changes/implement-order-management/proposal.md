# Proposal: Implement Order Management Tools

## Goal

Enable AI agents to perform trading operations (place, modify, cancel orders) and retrieve order/trade data using `moomoo-api`.

## What Changes

- `order-placement`: Place new trading orders (market, limit).
- `order-modification`: Modify parameters of existing orders (price, qty) and cancel orders.
- `order-retrieval`: Retrieve active orders, order history, and deal history.

## Why

To execute trading strategies and manage portfolios, the agent needs full control over the order lifecycle. The `moomoo-api` provides `OpenSecTradeContext` for this. This change implements the necessary tools to expose these trading capabilities to the agent.
