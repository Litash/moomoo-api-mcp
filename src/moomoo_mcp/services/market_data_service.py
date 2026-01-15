"""Market data service for accessing quote data via Moomoo API."""

from moomoo import OpenQuoteContext, RET_OK, SubType, KLType, AuType


class MarketDataService:
    """Service to access market data via OpenQuoteContext.

    This service provides methods to retrieve market quotes, historical K-line data,
    snapshots, and order book data. It uses the shared OpenQuoteContext from MoomooService.
    """

    def __init__(self, quote_ctx: OpenQuoteContext):
        """Initialize MarketDataService with an existing quote context.

        Args:
            quote_ctx: An already-connected OpenQuoteContext instance.
        """
        self.quote_ctx = quote_ctx

    def subscribe(self, codes: list[str], sub_types: list[SubType]) -> None:
        """Subscribe to real-time data for specified stocks and data types.

        Args:
            codes: List of stock codes (e.g., ['US.AAPL', 'HK.00700']).
            sub_types: List of subscription types (e.g., [SubType.QUOTE, SubType.ORDER_BOOK]).

        Raises:
            RuntimeError: If subscription fails.
        """
        if not self.quote_ctx:
            raise RuntimeError("Quote context not connected")

        ret, err = self.quote_ctx.subscribe(codes, sub_types, subscribe_push=False)
        if ret != RET_OK:
            raise RuntimeError(f"subscribe failed: {err}")

    def get_stock_quote(self, codes: list[str]) -> list[dict]:
        """Get real-time quotes for stocks.

        This method automatically subscribes to the stocks before fetching quotes.
        Returns current price, open, high, low, close, volume and other quote data.

        Args:
            codes: List of stock codes (e.g., ['US.AAPL']).

        Returns:
            List of quote dictionaries with price, volume, and other quote fields.

        Raises:
            RuntimeError: If quote retrieval fails.
        """
        if not self.quote_ctx:
            raise RuntimeError("Quote context not connected")

        # Auto-subscribe before getting quotes
        self.subscribe(codes, [SubType.QUOTE])

        ret, data = self.quote_ctx.get_stock_quote(codes)
        if ret != RET_OK:
            raise RuntimeError(f"get_stock_quote failed: {data}")

        return data.to_dict("records")

    def get_historical_klines(
        self,
        code: str,
        ktype: str = "K_DAY",
        start: str | None = None,
        end: str | None = None,
        max_count: int = 100,
        autype: str = "QFQ",
    ) -> list[dict]:
        """Get historical candlestick (K-line) data.

        Args:
            code: Stock code (e.g., 'US.AAPL').
            ktype: K-line type. Options: K_1M, K_3M, K_5M, K_15M, K_30M, K_60M,
                   K_DAY, K_WEEK, K_MON, K_QUARTER, K_YEAR.
            start: Start date (YYYY-MM-DD format). Defaults to 365 days before end.
            end: End date (YYYY-MM-DD format). Defaults to today.
            max_count: Maximum number of candles to return (default 100).
            autype: Adjustment type. Options: QFQ (forward), HFQ (backward), NONE.

        Returns:
            List of K-line dictionaries with time_key, open, high, low, close, volume.

        Raises:
            RuntimeError: If K-line retrieval fails.
        """
        if not self.quote_ctx:
            raise RuntimeError("Quote context not connected")

        # Convert string ktype to enum
        ktype_enum = getattr(KLType, ktype, KLType.K_DAY)
        autype_enum = getattr(AuType, autype, AuType.QFQ)

        ret, data, _ = self.quote_ctx.request_history_kline(
            code=code,
            start=start,
            end=end,
            ktype=ktype_enum,
            autype=autype_enum,
            max_count=max_count,
        )
        if ret != RET_OK:
            raise RuntimeError(f"request_history_kline failed: {data}")

        return data.to_dict("records")

    def get_market_snapshot(self, codes: list[str]) -> list[dict]:
        """Get market snapshot for multiple stocks.

        This is efficient for batch queries and does not require subscription.
        Returns current price, change, volume, and comprehensive market data.

        Args:
            codes: List of stock codes (up to 400). E.g., ['US.AAPL', 'US.TSLA'].

        Returns:
            List of snapshot dictionaries with last_price, open_price, high_price,
            low_price, prev_close_price, volume, turnover, and more.

        Raises:
            RuntimeError: If snapshot retrieval fails.
        """
        if not self.quote_ctx:
            raise RuntimeError("Quote context not connected")

        if not codes:
            return []

        ret, data = self.quote_ctx.get_market_snapshot(codes)
        if ret != RET_OK:
            raise RuntimeError(f"get_market_snapshot failed: {data}")

        return data.to_dict("records")

    def get_order_book(self, code: str, num: int = 10) -> dict:
        """Get order book (market depth) for a stock.

        This method automatically subscribes to the stock before fetching the order book.
        Returns bid and ask price levels with volumes.

        Args:
            code: Stock code (e.g., 'HK.00700').
            num: Number of price levels to return (default 10).

        Returns:
            Dictionary with 'code', 'Bid' (list of tuples), and 'Ask' (list of tuples).
            Each tuple contains (price, volume, order_count, order_details).

        Raises:
            RuntimeError: If order book retrieval fails.
        """
        if not self.quote_ctx:
            raise RuntimeError("Quote context not connected")

        # Auto-subscribe before getting order book
        self.subscribe([code], [SubType.ORDER_BOOK])

        ret, data = self.quote_ctx.get_order_book(code, num=num)
        if ret != RET_OK:
            raise RuntimeError(f"get_order_book failed: {data}")

        return data
