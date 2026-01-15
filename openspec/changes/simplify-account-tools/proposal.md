# Simplify Account Tools

## Why

Refactor account tools to remove ambiguous parameters and provide a unified view of account status. This reduces the cognitive load on the AI agent by enforcing a single way to identify accounts and providing a comprehensive snapshot tool.

## What Changes

- Remove `acc_index` parameter from all account tools to enforce usage of `acc_id`.
- Introduce `get_account_summary` tool that combines assets and positions.
- Ensure all account tools default `trd_env` to "SIMULATE" but clearly document "REAL" usage.

## Questions

- Should we completely remove `get_assets` and `get_positions` in favor of `get_account_summary`?
  - _Decision_: No, keep them for granular access (e.g., just checking positions without fetching asset data), but prompt `get_account_summary` as the primary discovery tool.
