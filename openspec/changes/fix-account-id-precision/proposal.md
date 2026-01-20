# Change: Fix Account ID Precision Loss

## Why

Large 64-bit integer Account IDs (e.g., `283726802397238513`) are suffering from precision loss during JSON serialization/deserialization when treated as numbers in MCP tool calls. This results in API errors like "Nonexisting acc_id" because the ID is rounded to a float representation (e.g., `283726802397239000`).

## What Changes

- Update all MCP tool definitions to accept `acc_id` as `str` (or `int | str`, preferring `str` for large IDs).
- Update internal service calls to handle string `acc_id` by converting to `int` where necessary for the SDK, or keeping as `int` if the SDK handles it, ensuring the tool interface strictly uses `str` or handles input safely.
- **BREAKING**: While `int` will still be accepted for backward compatibility where possible, the canonical type for `acc_id` in tools will become `str` to ensure precision.

## Impact

- Affected specs: `account-info`
- Affected code:
  - `src/moomoo_mcp/tools/account.py`
  - `src/moomoo_mcp/tools/trading.py`
  - `src/moomoo_mcp/services/trade_service.py` (if type validation exists)
