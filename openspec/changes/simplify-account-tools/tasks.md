# Tasks: Simplify Account Tools

1. [x] Remove `acc_index` from `TradeService` in `src/moomoo_mcp/services/trade_service.py`.
2. [x] Remove `acc_index` from `account.py` tools.
3. [x] Implement `get_account_summary` in `account.py` (orchestrated tool) or `TradeService` (service method).
   - _Decision_: Implement in `account.py` as it orchestrates service calls.
4. [x] Update unit tests to reflect removal of `acc_index`.
5. [x] Change `trd_env` default from `SIMULATE` to `REAL` and update AI agent guidance.
