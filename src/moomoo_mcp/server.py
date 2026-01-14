from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from moomoo_mcp.services.base_service import MoomooService
from moomoo_mcp.services.trade_service import TradeService


@dataclass
class AppContext:
    """Application context with typed dependencies."""
    moomoo_service: MoomooService
    trade_service: TradeService


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage moomoo connections lifecycle."""
    moomoo_service = MoomooService()
    moomoo_service.connect()

    trade_service = TradeService()
    trade_service.connect()

    try:
        yield AppContext(moomoo_service=moomoo_service, trade_service=trade_service)
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

def main():
    """Entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()
