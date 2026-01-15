import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from moomoo_mcp.services.base_service import MoomooService
from moomoo_mcp.services.market_data_service import MarketDataService
from moomoo_mcp.services.trade_service import TradeService

logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context with typed dependencies."""
    moomoo_service: MoomooService
    trade_service: TradeService
    market_data_service: MarketDataService


def _auto_unlock_trade(trade_service: TradeService) -> None:
    """Attempt to auto-unlock trade using environment variables.

    Reads MOOMOO_TRADE_PASSWORD (plain text, preferred) or MOOMOO_TRADE_PASSWORD_MD5.
    Logs status and handles failures gracefully without crashing.
    """
    password = os.environ.get("MOOMOO_TRADE_PASSWORD")
    password_md5 = os.environ.get("MOOMOO_TRADE_PASSWORD_MD5")

    if not password and not password_md5:
        logger.info(
            "No trade password configured (MOOMOO_TRADE_PASSWORD or "
            "MOOMOO_TRADE_PASSWORD_MD5 not set). Running in SIMULATE-only mode."
        )
        return

    try:
        # Must fetch account list before unlock to initialize account context
        accounts = trade_service.get_accounts()
        logger.info(f"Found {len(accounts)} trading account(s)")

        if password:
            trade_service.unlock_trade(password=password)
            logger.info("Trade unlocked successfully. REAL account access enabled.")
        else:
            trade_service.unlock_trade(password_md5=password_md5)
            logger.info("Trade unlocked successfully (via MD5). REAL account access enabled.")
    except RuntimeError as e:
        logger.warning(
            f"Failed to unlock trade: {e}. "
            "REAL account access will not be available. "
            "Use unlock_trade tool to retry manually."
        )


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage moomoo connections lifecycle."""
    moomoo_service = MoomooService()
    moomoo_service.connect()

    # Read security firm from environment (e.g., FUTUSG for Singapore, FUTUSECURITIES for HK)
    security_firm = os.environ.get("MOOMOO_SECURITY_FIRM")
    if security_firm:
        logger.info(f"Using security firm: {security_firm}")

    trade_service = TradeService(security_firm=security_firm)
    trade_service.connect()

    # Auto-unlock trade if password is configured in environment
    _auto_unlock_trade(trade_service)

    # Create market data service using the shared quote context
    market_data_service = MarketDataService(quote_ctx=moomoo_service.quote_ctx)

    try:
        yield AppContext(
            moomoo_service=moomoo_service,
            trade_service=trade_service,
            market_data_service=market_data_service,
        )
    finally:
        trade_service.close()
        moomoo_service.close()

mcp = FastMCP(
    "Moomoo Trading",
    lifespan=app_lifespan,
    dependencies=["moomoo-api", "pandas"] 
)

# Import tools to register them
import moomoo_mcp.tools.system
import moomoo_mcp.tools.account
import moomoo_mcp.tools.market_data
import moomoo_mcp.tools.trading

def main():
    """Entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
