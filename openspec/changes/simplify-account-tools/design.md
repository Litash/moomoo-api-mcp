# Design: Simplify Account Tools

## Problem

The current account tools offer two ways to select an account: `acc_id` (explicit) and `acc_index` (implicit/relative). This ambiguity confuses AI agents, leading to potential errors where the wrong account is selected if the order of accounts changes. Additionally, fetching a complete account state requires multiple tool calls (`get_assets` and `get_positions`), increasing context usage and latency.

## Solution

### 1. Enforce Explicit Account Identification

- **Change**: Remove the `acc_index` parameter from all `TradeService` methods and MCP tools.
- **Workflow**: Agents must effectively call `get_accounts()` first to obtain `acc_id`s, then use those IDs for subsequent operations. This enforces a deterministic workflow.

### 2. Unified Account Summary

- **Change**: specific `get_account_summary` tool.
- **Data**: Returns a dictionary containing `assets` (from `get_assets`) and `positions` (from `get_positions`).

## Trade-offs

- **Latency**: `get_account_summary` might be slightly slower than just `get_assets`, but saves a round trip.
- **Portability**: Agents trained to use `acc_index` (if any) will break. However, this is a new project, so breaking changes are acceptable for better architecture.
