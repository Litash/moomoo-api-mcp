
"""Market data tools for retrieving stock quotes, K-lines, snapshots, and order book."""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from moomoo_mcp.server import AppContext, mcp


@mcp.tool()
async def get_stock_quote(
    ctx: Context[ServerSession, AppContext],
    codes: list[str],
) -> list[dict]:
    """Get real-time stock quotes for specified codes.

    Returns current price, open, high, low, volume, and other quote data.
    Automatically subscribes to the stocks before fetching quotes.

    Args:
        codes: List of stock codes (e.g., ['US.AAPL', 'HK.00700']).

    Returns:
        List of quote dictionaries containing:
        - code: Stock code
        - last_price: Latest price
        - open_price: Open price
        - high_price: High price
        - low_price: Low price
        - prev_close_price: Previous close
        - volume: Trading volume
        - turnover: Turnover amount
        - And other quote fields
    """
    market_data_service = ctx.request_context.lifespan_context.market_data_service
    quotes = market_data_service.get_stock_quote(codes)
    await ctx.info(f"Retrieved quotes for {len(codes)} stocks")
    return quotes


@mcp.tool()
async def get_historical_klines(
    ctx: Context[ServerSession, AppContext],
    code: str,
    ktype: str = "K_DAY",
    start: str | None = None,
    end: str | None = None,
    max_count: int = 100,
    autype: str = "QFQ",
) -> list[dict]:
    """Get historical candlestick (K-line) data for a stock.

    Returns OHLCV (Open, High, Low, Close, Volume) data for technical analysis.

    Args:
        code: Stock code (e.g., 'US.AAPL').
        ktype: K-line type. Options:
            - K_1M: 1 minute
            - K_3M: 3 minutes
            - K_5M: 5 minutes
            - K_15M: 15 minutes
            - K_30M: 30 minutes
            - K_60M: 60 minutes
            - K_DAY: Daily (default)
            - K_WEEK: Weekly
            - K_MON: Monthly
            - K_QUARTER: Quarterly
            - K_YEAR: Yearly
        start: Start date in YYYY-MM-DD format. Defaults to 365 days before end.
        end: End date in YYYY-MM-DD format. Defaults to today.
        max_count: Maximum number of candles to return (default 100, max 1000).
        autype: Adjustment type for splits/dividends:
            - QFQ: Forward adjustment (default)
            - HFQ: Backward adjustment
            - NONE: No adjustment

    Returns:
        List of K-line dictionaries containing:
        - time_key: Candlestick timestamp
        - open: Open price
        - high: High price
        - low: Low price
        - close: Close price
        - volume: Volume
        - turnover: Turnover
        - change_rate: Price change rate
    """
    market_data_service = ctx.request_context.lifespan_context.market_data_service
    klines = market_data_service.get_historical_klines(
        code=code,
        ktype=ktype,
        start=start,
        end=end,
        max_count=max_count,
        autype=autype,
    )
    await ctx.info(f"Retrieved {len(klines)} K-lines for {code}")
    return klines


@mcp.tool()
async def get_market_snapshot(
    ctx: Context[ServerSession, AppContext],
    codes: list[str],
) -> list[dict]:
    """Get market snapshot for multiple stocks efficiently.

    This is ideal for checking current status of a watchlist without subscription.
    Returns comprehensive market data including price, volume, and fundamentals.

    Args:
        codes: List of stock codes (up to 400). E.g., ['US.AAPL', 'US.TSLA', 'HK.00700'].

    Returns:
        List of snapshot dictionaries containing:
        - code: Stock code
        - name: Stock name
        - last_price: Latest price
        - open_price: Open price
        - high_price: High price
        - low_price: Low price
        - prev_close_price: Previous close
        - volume: Trading volume
        - turnover: Turnover amount
        - turnover_rate: Turnover rate (%)
        - pe_ratio: P/E ratio
        - pb_ratio: P/B ratio
        - And many more fields
    """
    market_data_service = ctx.request_context.lifespan_context.market_data_service
    snapshots = market_data_service.get_market_snapshot(codes)
    await ctx.info(f"Retrieved snapshots for {len(codes)} stocks")
    return snapshots


@mcp.tool()
async def get_order_book(
    ctx: Context[ServerSession, AppContext],
    code: str,
    num: int = 10,
) -> dict:
    """Get order book (market depth) showing bid/ask price levels.

    Returns the top N bid and ask levels with prices and volumes.
    Useful for analyzing liquidity and market sentiment.
    Automatically subscribes to the stock before fetching order book.

    Args:
        code: Stock code (e.g., 'HK.00700', 'US.AAPL').
        num: Number of price levels to return (default 10).

    Returns:
        Dictionary containing:
        - code: Stock code
        - Bid: List of bid levels, each as (price, volume, order_count, details)
        - Ask: List of ask levels, each as (price, volume, order_count, details)
    """
    market_data_service = ctx.request_context.lifespan_context.market_data_service
    order_book = market_data_service.get_order_book(code, num=num)
    await ctx.info(f"Retrieved order book for {code} with {num} levels")
    return order_book


@mcp.tool()
async def get_user_security_group(
    ctx: Context[ServerSession, AppContext],
    group_type: int = 0,
) -> list[dict]:
    """Get list of user-defined security groups (watchlists).

    Returns the user's custom watchlist groups from the Moomoo app.

    Args:
        group_type: Type of groups to return. Options:
            - 0: All groups (default)
            - 1: Custom groups only
            - 2: System groups only

    Returns:
        List of group dictionaries containing:
        - group_name: Name of the group
        - group_id: Unique identifier for the group
    """
    market_data_service = ctx.request_context.lifespan_context.market_data_service
    groups = market_data_service.get_user_security_group(group_type=group_type)
    await ctx.info(f"Retrieved {len(groups)} security groups")
    return groups


@mcp.tool()
async def get_user_security(
    ctx: Context[ServerSession, AppContext],
    group_name: str,
) -> list[dict]:
    """Get list of securities in a specific user-defined group (watchlist).

    Returns all stocks/securities that the user has added to a specific watchlist.

    Args:
        group_name: Name of the security group (e.g., 'Favorites', 'Tech').

    Returns:
        List of security dictionaries containing:
        - code: Stock code (e.g., 'US.AAPL')
        - name: Stock name
        - lot_size: Lot size for trading
        - stock_type: Type of security
    """
    market_data_service = ctx.request_context.lifespan_context.market_data_service
    securities = market_data_service.get_user_security(group_name)
    await ctx.info(f"Retrieved {len(securities)} securities from group '{group_name}'")
    return securities
