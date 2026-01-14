"""Account tools for trading account information retrieval."""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from moomoo_mcp.server import AppContext, mcp


@mcp.tool()
async def get_accounts(
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Get list of trading accounts.

    Returns list of account dictionaries with acc_id, account type, etc.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    accounts = trade_service.get_accounts()
    await ctx.info(f"Retrieved {len(accounts)} accounts")
    return accounts


@mcp.tool()
async def get_assets(
    ctx: Context[ServerSession, AppContext],
    trd_env: str = "REAL",
    acc_id: int = 0,
    acc_index: int = 0,
    refresh_cache: bool = False,
    currency: str = "",
) -> dict:
    """Get account assets including cash, market value, buying power.

    Args:
        trd_env: Trading environment, 'REAL' or 'SIMULATE'.
        acc_id: Account ID. If 0, uses acc_index.
        acc_index: Account index (default first account).
        refresh_cache: Whether to refresh the cache.
        currency: Filter by currency.

    Returns:
        Dictionary with asset information.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    assets = trade_service.get_assets(
        trd_env=trd_env,
        acc_id=acc_id,
        acc_index=acc_index,
        refresh_cache=refresh_cache,
        currency=currency,
    )
    await ctx.info(f"Retrieved assets for account")
    return assets


@mcp.tool()
async def get_positions(
    ctx: Context[ServerSession, AppContext],
    code: str = "",
    pl_ratio_min: float | None = None,
    pl_ratio_max: float | None = None,
    trd_env: str = "REAL",
    acc_id: int = 0,
    acc_index: int = 0,
    refresh_cache: bool = False,
) -> list[dict]:
    """Get current positions in the trading account.

    Args:
        code: Filter by stock code.
        pl_ratio_min: Minimum profit/loss ratio filter.
        pl_ratio_max: Maximum profit/loss ratio filter.
        trd_env: Trading environment.
        acc_id: Account ID.
        acc_index: Account index.
        refresh_cache: Whether to refresh cache.

    Returns:
        List of position dictionaries.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    positions = trade_service.get_positions(
        code=code,
        pl_ratio_min=pl_ratio_min,
        pl_ratio_max=pl_ratio_max,
        trd_env=trd_env,
        acc_id=acc_id,
        acc_index=acc_index,
        refresh_cache=refresh_cache,
    )
    await ctx.info(f"Retrieved {len(positions)} positions")
    return positions


@mcp.tool()
async def get_max_tradable(
    ctx: Context[ServerSession, AppContext],
    order_type: str,
    code: str,
    price: float,
    order_id: str = "",
    adjust_limit: float = 0,
    trd_env: str = "REAL",
    acc_id: int = 0,
    acc_index: int = 0,
) -> dict:
    """Get maximum tradable quantity for a stock.

    Args:
        order_type: Order type (e.g., 'NORMAL', 'LIMIT', 'MARKET').
        code: Stock code (e.g., 'US.AAPL').
        price: Target price.
        order_id: Optional order ID for modification scenarios.
        adjust_limit: Adjust limit percentage.
        trd_env: Trading environment.
        acc_id: Account ID.
        acc_index: Account index.

    Returns:
        Dictionary with max buy/sell quantities.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    max_qty = trade_service.get_max_tradable(
        order_type=order_type,
        code=code,
        price=price,
        order_id=order_id,
        adjust_limit=adjust_limit,
        trd_env=trd_env,
        acc_id=acc_id,
        acc_index=acc_index,
    )
    await ctx.info(f"Retrieved max tradable for {code}")
    return max_qty


@mcp.tool()
async def get_margin_ratio(
    ctx: Context[ServerSession, AppContext],
    code_list: list[str],
) -> list[dict]:
    """Get margin ratio for stocks.

    Args:
        code_list: List of stock codes (e.g., ['US.AAPL', 'US.TSLA']).

    Returns:
        List of margin ratio dictionaries.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    ratios = trade_service.get_margin_ratio(code_list=code_list)
    await ctx.info(f"Retrieved margin ratios for {len(code_list)} stocks")
    return ratios


@mcp.tool()
async def get_cash_flow(
    ctx: Context[ServerSession, AppContext],
    clearing_date: str = "",
    trd_env: str = "REAL",
    acc_id: int = 0,
    acc_index: int = 0,
) -> list[dict]:
    """Get account cash flow history.

    Args:
        clearing_date: Filter by clearing date (YYYY-MM-DD format).
        trd_env: Trading environment.
        acc_id: Account ID.
        acc_index: Account index.

    Returns:
        List of cash flow record dictionaries.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    cash_flows = trade_service.get_cash_flow(
        clearing_date=clearing_date,
        trd_env=trd_env,
        acc_id=acc_id,
        acc_index=acc_index,
    )
    await ctx.info(f"Retrieved {len(cash_flows)} cash flow records")
    return cash_flows


@mcp.tool()
async def unlock_trade(
    ctx: Context[ServerSession, AppContext],
    password: str | None = None,
    password_md5: str | None = None,
) -> dict:
    """Unlock trade for trading operations.

    Required before executing trades or accessing certain sensitive data.

    Args:
        password: Plain text trade password.
        password_md5: MD5 hash of trade password (alternative to password).

    Returns:
        Success status dictionary.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    trade_service.unlock_trade(password=password, password_md5=password_md5)
    await ctx.info("Trade unlocked successfully")
    return {"status": "unlocked"}
