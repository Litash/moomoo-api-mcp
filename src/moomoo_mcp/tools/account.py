"""Account tools for trading account information retrieval."""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from moomoo_mcp.server import AppContext, mcp


@mcp.tool()
async def get_accounts(
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Get list of trading accounts.

    Returns list of account dictionaries with acc_id, trd_env (REAL/SIMULATE), etc.

    IMPORTANT: This returns both REAL and SIMULATE accounts. To access REAL account
    data via other tools (get_assets, get_positions, etc.), you must first call
    unlock_trade with the trading password.

    Returns:
        List of account dictionaries containing acc_id, trd_env, and other metadata.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    accounts = trade_service.get_accounts()
    await ctx.info(f"Retrieved {len(accounts)} accounts")
    return accounts


@mcp.tool()
async def get_account_summary(
    ctx: Context[ServerSession, AppContext],
    trd_env: str = "REAL",
    acc_id: int = 0,
) -> dict:
    """Get complete account summary including assets and positions in one call.

    This is the recommended tool for getting a full view of an account's status.
    It combines get_assets and get_positions into a single response.

    IMPORTANT FOR AI AGENTS:
    - Default is REAL account. You MUST notify the user clearly that you are
      accessing their REAL trading account before proceeding.
    - For REAL accounts, you must call unlock_trade first with the trading password.
    - If user wants SIMULATE account, they must explicitly request it.

    Args:
        trd_env: Trading environment. 'REAL' (default, requires unlock_trade first)
            or 'SIMULATE' (no unlock needed, for testing).
        acc_id: Account ID. Must be obtained from get_accounts().

    Returns:
        Dictionary with 'assets' (cash, market_val, etc.) and 'positions' (list of holdings).
    """
    trade_service = ctx.request_context.lifespan_context.trade_service

    assets = trade_service.get_assets(trd_env=trd_env, acc_id=acc_id)
    positions = trade_service.get_positions(trd_env=trd_env, acc_id=acc_id)

    await ctx.info(f"Retrieved summary for {trd_env} account: {len(positions)} positions")

    return {
        "assets": assets,
        "positions": positions,
    }


@mcp.tool()
async def get_assets(
    ctx: Context[ServerSession, AppContext],
    trd_env: str = "REAL",
    acc_id: int = 0,
    refresh_cache: bool = False,
    currency: str = "",
) -> dict:
    """Get account assets including cash, market value, buying power.

    IMPORTANT FOR AI AGENTS:
    - Default is REAL account. You MUST notify the user clearly that you are
      accessing their REAL trading account before proceeding.
    - For REAL accounts, you must call unlock_trade first with the trading password.
    - If user wants SIMULATE account, they must explicitly request it.

    Args:
        trd_env: Trading environment. 'REAL' (default, requires unlock_trade first)
            or 'SIMULATE' (no unlock needed, for testing).
        acc_id: Account ID. Must be obtained from get_accounts().
        refresh_cache: Whether to refresh the cache.
        currency: Filter by currency.

    Returns:
        Dictionary with asset information including cash, market_val, total_assets, etc.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    assets = trade_service.get_assets(
        trd_env=trd_env,
        acc_id=acc_id,
        refresh_cache=refresh_cache,
        currency=currency,
    )
    await ctx.info(f"Retrieved assets for {trd_env} account")
    return assets


@mcp.tool()
async def get_positions(
    ctx: Context[ServerSession, AppContext],
    code: str = "",
    market: str = "",
    pl_ratio_min: float | None = None,
    pl_ratio_max: float | None = None,
    trd_env: str = "REAL",
    acc_id: int = 0,
    refresh_cache: bool = False,
) -> list[dict]:
    """Get current positions.

    IMPORTANT FOR AI AGENTS:
    - Default is REAL account. You MUST notify the user clearly that you are
      accessing their REAL trading account before proceeding.
    - For REAL accounts, you must call unlock_trade first with the trading password.
    - If user wants SIMULATE account, they must explicitly request it.

    Args:
        code: Filter by stock code (e.g., 'US.AAPL').
        market: Filter by market (e.g., 'US', 'HK', 'CN', 'SG', 'JP').
        pl_ratio_min: Minimum profit/loss ratio filter.
        pl_ratio_max: Maximum profit/loss ratio filter.
        trd_env: Trading environment. 'REAL' (default, requires unlock_trade first)
            or 'SIMULATE' (no unlock needed, for testing).
        acc_id: Account ID. Must be obtained from get_accounts().
        refresh_cache: Whether to refresh cache.

    Returns:
        List of position dictionaries with code, qty, cost_price, market_val, pl_ratio, etc.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    positions = trade_service.get_positions(
        code=code,
        market=market,
        pl_ratio_min=pl_ratio_min,
        pl_ratio_max=pl_ratio_max,
        trd_env=trd_env,
        acc_id=acc_id,
        refresh_cache=refresh_cache,
    )
    await ctx.info(f"Retrieved {len(positions)} positions from {trd_env} account")
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
) -> dict:
    """Get maximum tradable quantity for a stock.

    IMPORTANT FOR AI AGENTS:
    - Default is REAL account. You MUST notify the user clearly that you are
      accessing their REAL trading account before proceeding.
    - For REAL accounts, you must call unlock_trade first with the trading password.
    - If user wants SIMULATE account, they must explicitly request it.

    Args:
        order_type: Order type (e.g., 'NORMAL', 'LIMIT', 'MARKET').
        code: Stock code (e.g., 'US.AAPL').
        price: Target price for the order.
        order_id: Optional order ID for modification scenarios.
        adjust_limit: Adjust limit percentage.
        trd_env: Trading environment. 'REAL' (default, requires unlock_trade first)
            or 'SIMULATE' (no unlock needed, for testing).
        acc_id: Account ID. Must be obtained from get_accounts().

    Returns:
        Dictionary with max_cash_buy, max_cash_and_margin_buy, max_position_sell, etc.
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
    )
    await ctx.info(f"Retrieved max tradable for {code} in {trd_env} account")
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
) -> list[dict]:
    """Get account cash flow history.

    IMPORTANT FOR AI AGENTS:
    - Default is REAL account. You MUST notify the user clearly that you are
      accessing their REAL trading account before proceeding.
    - For REAL accounts, you must call unlock_trade first with the trading password.
    - If user wants SIMULATE account, they must explicitly request it.

    Args:
        clearing_date: Filter by clearing date (YYYY-MM-DD format).
        trd_env: Trading environment. 'REAL' (default, requires unlock_trade first)
            or 'SIMULATE' (no unlock needed, for testing).
        acc_id: Account ID. Must be obtained from get_accounts().

    Returns:
        List of cash flow record dictionaries.
    """
    trade_service = ctx.request_context.lifespan_context.trade_service
    cash_flows = trade_service.get_cash_flow(
        clearing_date=clearing_date,
        trd_env=trd_env,
        acc_id=acc_id,
    )
    await ctx.info(f"Retrieved {len(cash_flows)} cash flow records from {trd_env} account")
    return cash_flows



@mcp.tool()
async def unlock_trade(
    ctx: Context[ServerSession, AppContext],
    password: str | None = None,
    password_md5: str | None = None,
) -> dict:
    """Unlock trade to access REAL account data.

    IMPORTANT: You MUST call this tool before accessing REAL account data via other
    tools (get_assets, get_positions, get_max_tradable, get_cash_flow with trd_env='REAL').

    This is NOT required for SIMULATE accounts - they work without unlocking.

    Workflow for accessing REAL account data:
    1. First call unlock_trade(). It will try to use environment variables first.
       - Checks MOOMOO_TRADE_PASSWORD (plain text)
       - Checks MOOMOO_TRADE_PASSWORD_MD5 (md5 hash)
    2. If that fails or if you want to provide credentials explicitly, call
       unlock_trade(password='your_trading_password').
    3. Then call other tools with trd_env='REAL'.

    Args:
        password: Plain text trade password (the password you set in Moomoo app).
            If not provided, will look for MOOMOO_TRADE_PASSWORD env var.
        password_md5: MD5 hash of trade password (alternative to password).
            If not provided, will look for MOOMOO_TRADE_PASSWORD_MD5 env var.
            Provide either password or password_md5, not both.

    Returns:
        Success status dictionary with {'status': 'unlocked'}.

    Note:
        The unlock state is maintained for the session. You only need to call this
        once per session to access REAL account data.
    """
    import os

    # If no args provided, try env vars
    if not password and not password_md5:
        password = os.environ.get("MOOMOO_TRADE_PASSWORD")
        password_md5 = os.environ.get("MOOMOO_TRADE_PASSWORD_MD5")

    trade_service = ctx.request_context.lifespan_context.trade_service
    trade_service.unlock_trade(password=password, password_md5=password_md5)
    await ctx.info("Trade unlocked successfully - REAL account data is now accessible")
    return {"status": "unlocked", "message": "You can now access REAL account data by setting trd_env='REAL' in other tools"}
