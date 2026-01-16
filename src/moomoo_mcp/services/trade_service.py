"""Trade service for managing Moomoo trading context and account operations."""

from moomoo import OpenSecTradeContext, RET_OK, SecurityFirm, TrdMarket


class TradeService:
    """Service to manage Moomoo Trade API connections and account operations."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 11111,
        security_firm: str | None = None,
    ):
        """Initialize TradeService.

        Args:
            host: Host address of OpenD gateway.
            port: Port number of OpenD gateway.
            security_firm: Securities firm identifier (e.g., 'FUTUSG' for Singapore,
                'FUTUSECURITIES' for HK). If None, no filter is applied.
        """
        self.host = host
        self.port = port
        self.security_firm = security_firm
        self.trade_ctx: OpenSecTradeContext | None = None

    def connect(self) -> None:
        """Initialize connection to OpenD trade context."""
        # Build kwargs for OpenSecTradeContext
        kwargs = {"host": self.host, "port": self.port}

        # Add security_firm if specified
        if self.security_firm:
            # Convert string to SecurityFirm enum
            firm_enum = getattr(SecurityFirm, self.security_firm, None)
            if firm_enum:
                kwargs["security_firm"] = firm_enum

        self.trade_ctx = OpenSecTradeContext(**kwargs)

    def close(self) -> None:
        """Close trade context connection."""
        if self.trade_ctx:
            self.trade_ctx.close()
            self.trade_ctx = None

    def get_accounts(self) -> list[dict]:
        """Get list of trading accounts.

        Returns:
            List of account dictionaries with acc_id, trd_env, etc.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.get_acc_list()
        if ret != RET_OK:
            raise RuntimeError(f"get_acc_list failed: {data}")

        return data.to_dict("records")

    def get_assets(
        self,
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
        refresh_cache: bool = False,
        currency: str = "",
    ) -> dict:
        """Get account assets (cash, market value, etc.).

        Args:
            trd_env: Trading environment, 'REAL' or 'SIMULATE'.
            acc_id: Account ID. Must be obtained from get_accounts().
            refresh_cache: Whether to refresh the cache.
            currency: Filter by currency.

        Returns:
            Dictionary with asset information.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.accinfo_query(
            trd_env=trd_env,
            acc_id=acc_id,
            refresh_cache=refresh_cache,
            currency=currency,
        )
        if ret != RET_OK:
            raise RuntimeError(f"accinfo_query failed: {data}")

        records = data.to_dict("records")
        return records[0] if records else {}

    def get_positions(
        self,
        code: str = "",
        market: str = "",
        pl_ratio_min: float | None = None,
        pl_ratio_max: float | None = None,
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
        refresh_cache: bool = False,
    ) -> list[dict]:
        """Get current positions.

        Args:
            code: Filter by stock code.
            market: Filter by market (e.g., 'US', 'HK', 'CN', 'SG', 'JP').
            pl_ratio_min: Minimum profit/loss ratio filter.
            pl_ratio_max: Maximum profit/loss ratio filter.
            trd_env: Trading environment.
            acc_id: Account ID. Must be obtained from get_accounts().
            refresh_cache: Whether to refresh cache.

        Returns:
            List of position dictionaries.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        # Map market string to TrdMarket enum
        # Note: CN is for A-share simulation only; HKCC for Stock Connect (live only)
        market_map = {
            "US": TrdMarket.US,
            "HK": TrdMarket.HK,
            "CN": TrdMarket.CN,
            "HKCC": TrdMarket.HKCC,
            "SG": TrdMarket.SG,
            "JP": TrdMarket.JP,
        }
        position_market = TrdMarket.NONE
        if market:
            try:
                # Try direct map first
                position_market = market_map.get(market.upper())
                if position_market is None:
                    # Try to use getattr for other potential values
                    position_market = getattr(TrdMarket, market.upper())
            except AttributeError:
                position_market = TrdMarket.NONE

        ret, data = self.trade_ctx.position_list_query(
            code=code,
            position_market=position_market,
            pl_ratio_min=pl_ratio_min,
            pl_ratio_max=pl_ratio_max,
            trd_env=trd_env,
            acc_id=acc_id,
            refresh_cache=refresh_cache,
        )
        if ret != RET_OK:
            raise RuntimeError(f"position_list_query failed: {data}")

        return data.to_dict("records")

    def get_max_tradable(
        self,
        order_type: str,
        code: str,
        price: float,
        order_id: str = "",
        adjust_limit: float = 0,
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
    ) -> dict:
        """Get maximum tradable quantity for a stock.

        Args:
            order_type: Order type string (e.g., 'NORMAL').
            code: Stock code.
            price: Target price.
            order_id: Optional order ID for modification.
            adjust_limit: Adjust limit percentage.
            trd_env: Trading environment.
            acc_id: Account ID. Must be obtained from get_accounts().

        Returns:
            Dictionary with max quantities for buy/sell.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.acctradinginfo_query(
            order_type=order_type,
            code=code,
            price=price,
            order_id=order_id,
            adjust_limit=adjust_limit,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if ret != RET_OK:
            raise RuntimeError(f"acctradinginfo_query failed: {data}")

        records = data.to_dict("records")
        return records[0] if records else {}

    def get_margin_ratio(self, code_list: list[str]) -> list[dict]:
        """Get margin ratio for stocks.

        Args:
            code_list: List of stock codes.

        Returns:
            List of margin ratio dictionaries.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.get_margin_ratio(code_list=code_list)
        if ret != RET_OK:
            raise RuntimeError(f"get_margin_ratio failed: {data}")

        return data.to_dict("records")

    def get_cash_flow(
        self,
        clearing_date: str = "",
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
    ) -> list[dict]:
        """Get account cash flow history.

        Args:
            clearing_date: Filter by clearing date (YYYY-MM-DD).
            trd_env: Trading environment.
            acc_id: Account ID. Must be obtained from get_accounts().

        Returns:
            List of cash flow record dictionaries.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.get_acc_cash_flow(
            clearing_date=clearing_date,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if ret != RET_OK:
            raise RuntimeError(f"get_acc_cash_flow failed: {data}")

        return data.to_dict("records")

    def unlock_trade(
        self, password: str | None = None, password_md5: str | None = None
    ) -> None:
        """Unlock trade for trading operations.

        Args:
            password: Plain text trade password.
            password_md5: MD5 hash of trade password (alternative to password).

        Raises:
            RuntimeError: If unlock fails.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.unlock_trade(
            password=password,
            password_md5=password_md5,
            is_unlock=True,
        )
        if ret != RET_OK:
            raise RuntimeError(f"unlock_trade failed: {data}")

    def place_order(
        self,
        code: str,
        price: float,
        qty: int,
        trd_side: str,
        order_type: str = "NORMAL",
        time_in_force: str = "DAY",
        adjust_limit: float = 0,
        aux_price: float | None = None,
        trail_type: str | None = None,
        trail_value: float | None = None,
        trail_spread: float | None = None,
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
        remark: str = "",
    ) -> dict:
        """Place a new trading order.

        Args:
            code: Stock code (e.g., 'US.AAPL').
            price: Order price.
            qty: Order quantity.
            trd_side: Trade side ('BUY' or 'SELL').
            order_type: Order type ('NORMAL', 'MARKET', etc.).
            time_in_force: Time in force ('DAY' or 'GTC'). Defaults to 'DAY'.
            adjust_limit: Adjust limit percentage.
            aux_price: Trigger price for stop/if-touched order types.
            trail_type: Trailing type ('RATIO' or 'AMOUNT') for trailing stop types.
            trail_value: Trailing value (ratio or amount) for trailing stop types.
            trail_spread: Optional trailing spread for trailing stop limit types.
            trd_env: Trading environment ('REAL' or 'SIMULATE').
            acc_id: Account ID. Must be obtained from get_accounts().
            remark: Order remark/note.

        Returns:
            Dictionary with order details including order_id.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        stop_order_types = {
            "STOP",
            "STOP_LIMIT",
            "MARKET_IF_TOUCHED",
            "LIMIT_IF_TOUCHED",
        }
        trailing_order_types = {"TRAILING_STOP", "TRAILING_STOP_LIMIT"}
        if order_type in stop_order_types and aux_price is None:
            raise ValueError("aux_price is required for stop/if-touched order types")
        if order_type in trailing_order_types and (
            trail_type is None or trail_value is None
        ):
            raise ValueError(
                "trail_type and trail_value are required for trailing stop order types"
            )

        ret, data = self.trade_ctx.place_order(
            price=price,
            qty=qty,
            code=code,
            trd_side=trd_side,
            order_type=order_type,
            time_in_force=time_in_force,
            adjust_limit=adjust_limit,
            aux_price=aux_price,
            trail_type=trail_type,
            trail_value=trail_value,
            trail_spread=trail_spread,
            trd_env=trd_env,
            acc_id=acc_id,
            remark=remark,
        )
        if ret != RET_OK:
            raise RuntimeError(f"place_order failed: {data}")

        records = data.to_dict("records")
        return records[0] if records else {}

    def modify_order(
        self,
        order_id: str,
        modify_order_op: str,
        qty: int | None = None,
        price: float | None = None,
        adjust_limit: float = 0,
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
    ) -> dict:
        """Modify an existing order.

        Args:
            order_id: Order ID to modify.
            modify_order_op: Modification operation ('NORMAL', 'CANCEL', 'DISABLE', 'ENABLE', 'DELETE').
            qty: New quantity (optional).
            price: New price (optional).
            adjust_limit: Adjust limit percentage.
            trd_env: Trading environment.
            acc_id: Account ID.

        Returns:
            Dictionary with modified order details.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.modify_order(
            modify_order_op=modify_order_op,
            order_id=order_id,
            qty=qty,
            price=price,
            adjust_limit=adjust_limit,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if ret != RET_OK:
            raise RuntimeError(f"modify_order failed: {data}")

        records = data.to_dict("records")
        return records[0] if records else {}

    def cancel_order(
        self,
        order_id: str,
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
    ) -> dict:
        """Cancel an existing order.

        Convenience wrapper around modify_order with CANCEL operation.

        Args:
            order_id: Order ID to cancel.
            trd_env: Trading environment.
            acc_id: Account ID.

        Returns:
            Dictionary with cancelled order details.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.modify_order(
            modify_order_op="CANCEL",
            order_id=order_id,
            qty=0,
            price=0,
            adjust_limit=0,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if ret != RET_OK:
            raise RuntimeError(f"cancel_order failed: {data}")

        records = data.to_dict("records")
        return records[0] if records else {}

    def get_orders(
        self,
        code: str = "",
        status_filter_list: list[str] | None = None,
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
        refresh_cache: bool = False,
    ) -> list[dict]:
        """Get list of today's orders.

        Args:
            code: Filter by stock code.
            status_filter_list: Filter by order statuses.
            trd_env: Trading environment.
            acc_id: Account ID.
            refresh_cache: Whether to refresh cache.

        Returns:
            List of order dictionaries.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.order_list_query(
            code=code,
            status_filter_list=status_filter_list,
            trd_env=trd_env,
            acc_id=acc_id,
            refresh_cache=refresh_cache,
        )
        if ret != RET_OK:
            raise RuntimeError(f"order_list_query failed: {data}")

        return data.to_dict("records")

    def get_deals(
        self,
        code: str = "",
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
        refresh_cache: bool = False,
    ) -> list[dict]:
        """Get list of today's deals (executed trades).

        Args:
            code: Filter by stock code.
            trd_env: Trading environment.
            acc_id: Account ID.
            refresh_cache: Whether to refresh cache.

        Returns:
            List of deal dictionaries.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.deal_list_query(
            code=code,
            trd_env=trd_env,
            acc_id=acc_id,
            refresh_cache=refresh_cache,
        )
        if ret != RET_OK:
            raise RuntimeError(f"deal_list_query failed: {data}")

        return data.to_dict("records")

    def get_history_orders(
        self,
        code: str = "",
        status_filter_list: list[str] | None = None,
        start: str = "",
        end: str = "",
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
    ) -> list[dict]:
        """Get historical orders.

        Args:
            code: Filter by stock code.
            status_filter_list: Filter by order statuses.
            start: Start date (YYYY-MM-DD).
            end: End date (YYYY-MM-DD).
            trd_env: Trading environment.
            acc_id: Account ID.

        Returns:
            List of historical order dictionaries.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.history_order_list_query(
            code=code,
            status_filter_list=status_filter_list,
            start=start,
            end=end,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if ret != RET_OK:
            raise RuntimeError(f"history_order_list_query failed: {data}")

        return data.to_dict("records")

    def get_history_deals(
        self,
        code: str = "",
        start: str = "",
        end: str = "",
        trd_env: str = "SIMULATE",
        acc_id: int = 0,
    ) -> list[dict]:
        """Get historical deals (executed trades).

        Args:
            code: Filter by stock code.
            start: Start date (YYYY-MM-DD).
            end: End date (YYYY-MM-DD).
            trd_env: Trading environment.
            acc_id: Account ID.

        Returns:
            List of historical deal dictionaries.
        """
        if not self.trade_ctx:
            raise RuntimeError("Trade context not connected")

        ret, data = self.trade_ctx.history_deal_list_query(
            code=code,
            start=start,
            end=end,
            trd_env=trd_env,
            acc_id=acc_id,
        )
        if ret != RET_OK:
            raise RuntimeError(f"history_deal_list_query failed: {data}")

        return data.to_dict("records")
