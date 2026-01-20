## 1. Implementation

- [ ] 1.1 Update `src/moomoo_mcp/tools/account.py` tool signatures to accept `acc_id: str | int` (defaulting to strict string handling in logic or converting safely).
- [ ] 1.2 Update `src/moomoo_mcp/tools/trading.py` tool signatures to accept `acc_id: str | int`.
- [ ] 1.3 Update `src/moomoo_mcp/services/trade_service.py` to handle string `acc_id` inputs if strict typing prevents it.
- [ ] 1.4 Update `tests/test_tools/test_account.py` to use string account IDs and add a specific test case for a large 64-bit integer ID.
- [ ] 1.5 Update `tests/test_tools/test_trading.py` (if exists) or add tests to verify `trading` tools with string IDs.
