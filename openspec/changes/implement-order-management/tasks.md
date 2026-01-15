# Tasks: Implement Order Management

1.  **Update TradeService Tests**
    - [x] Update `tests/test_services/test_trade_service.py` to include tests for:
      - `place_order`
      - `modify_order`
      - `cancel_order` (wrapper)
      - `get_orders`
      - `get_deals`
      - `get_history_orders`
      - `get_history_deals`
      - Mock `OpenSecTradeContext` responses for these methods.

2.  **Implement TradeService Methods**
    - [x] Modify `src/moomoo_mcp/services/trade_service.py`:
      - Add `place_order`: Call `trd_ctx.place_order`.
      - Add `modify_order`: Call `trd_ctx.modify_order`.
      - Add `cancel_order`: Call `trd_ctx.modify_order` with `CANCEL` op.
      - Add `get_orders`: Call `trd_ctx.order_list_query`.
      - Add `get_deals`: Call `trd_ctx.deal_list_query`.
      - Add `get_history_orders`: Call `trd_ctx.history_order_list_query`.
      - Add `get_history_deals`: Call `trd_ctx.history_deal_list_query`.
      - Ensure proper error handling (raise RuntimeError on ret code failure).

3.  **Implement Trading Tools**
    - [x] Create `src/moomoo_mcp/tools/trading.py`.
    - [x] Implement `place_order` tool:
      - Args: `code`, `side`, `qty`, `price`, `order_type`, `adjust_limit`, `trd_env`, `acc_id`.
      - Use `TradeService.place_order`.
    - [x] Implement `modify_order` tool:
      - Args: `order_id`, `modify_order_op`, `qty`, `price`, `adjust_limit`, `trd_env`, `acc_id`.
    - [x] Implement `cancel_order` tool:
      - Args: `order_id`, `trd_env`, `acc_id`.
    - [x] Implement `get_orders` tool:
      - Args: `trd_env`, `acc_id`, `code` (optional filter).
    - [x] Implement `get_deals` tool:
      - Args: `trd_env`, `acc_id`, `code` (optional filter).

4.  **Register Tools**
    - [x] Update `src/moomoo_mcp/server.py` (or `__init__.py` in tools) to include `trading.py` tools.

5.  **Verification**
    - [x] Run `pytest tests/test_services/test_trade_service.py`. (34 passed)
    - [x] Manual verification via MCP Inspector (optional, if environment available).
