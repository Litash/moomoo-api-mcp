# Design: Order Management Tools

## Context

We need to provide tools for the AI agent to manage trading orders. Moomoo API provides `OpenSecTradeContext` for this.

## Architectural Decisions

### 1. Synchronous vs Asynchronous

The `moomoo-api` Python SDK methods (`place_order`, etc.) are synchronous blocking calls that return `(ret_code, data)`.
Since `FastMCP` supports `async def`, we will wrap these blocking calls. Ideally, we should offload them to a thread pool if they block the event loop significantly, but for now, calling them directly within `async def` (which might block the loop) is acceptable for low concurrency usage unless `moomoo-api` offers an async version (it doesn't seem to).
_Refinement_: If `moomoo-api` operations take time (network RTT), blocking the main loop is bad. `FastMCP` might handle it, but standard `asyncio` doesn't like blocking calls.
_Decision_: We will invoke `TradeService` methods directly. If performance becomes an issue, we can use `run_in_executor`. For now, direct call.

### 2. Default Trading Environment

Requirement: Default to `TrdEnv.REAL`.
Tools will accept an optional `trd_env` parameter, defaulting to `"REAL"`.
_Constraint_: Users must be careful. We should add a disclaimer or require explicit confirmation for "REAL" in the tool description, but the tool logic itself will default to REAL as per user rules.

### 3. Tool Interface

We will map `moomoo-api` parameters to tool arguments.

- `place_order`: `code`, `side`, `qty`, `price`, `order_type`, `adjust_limit`, `trd_env`, `acc_id`.
- `modify_order`: `order_id`, `modify_order_op`, `qty`, `price`, `adjust_limit`, `trd_env`, `acc_id`.
- `cancel_order`: specific tool wrapping `modify_order` with `CANCEL` op, for convenience.
- `get_orders`: `trd_env`, `acc_id`.
- `get_deals`: `trd_env`, `acc_id`.

### 4. TradeService Extensions

We will add the following methods to `TradeService`:

- `place_order(...)`
- `modify_order(...)`
- `cancel_order(...)`
- `get_orders(...)`
- `get_max_order_quantity(...)` (Use existing `get_max_tradable`, maybe alias it or just use it directly).
- `get_deals(...)`
- `get_history_orders(...)`
- `get_history_deals(...)`

### 5. Safety & Confirmation

Requirement: The tool must instruct the AI Agent to ask for user confirmation before taking any action on orders, especially in the `REAL` environment.
_Implementation_:

- The docstrings for `place_order`, `modify_order`, and `cancel_order` tools will explicitly include a directive: "CRITICAL: You MUST ask the user for explicit confirmation before calling this tool, especially if `trd_env` is 'REAL'. Display the full order details to the user for verification."
- This prompts the LLM to verify with the user _before_ it even calls the tool.

### 6. Error Handling

- Check `ret_code`. If `ret_code != RET_OK`, raise `RuntimeError` with the error message.
- The Tool layer will catch exceptions and return error strings to the model.

## Alternatives Considered

- **Separate Cancel Tool vs Modify Tool**: `cancel_order` is just a special case of `modify_order`. However, a separate tool is semantically clearer for the LLM. We will provide both or a dedicated `cancel_order` tool.
- **Async API**: Building a custom async wrapper around `OpenD`. Too complex for now.
