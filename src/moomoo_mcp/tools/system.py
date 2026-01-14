from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from moomoo_mcp.server import AppContext, mcp

@mcp.tool()
async def check_health(
    ctx: Context[ServerSession, AppContext]
) -> dict[str, str]:
    """Check connectivity to Moomoo and MCP server health.

    Returns:
        Dictionary containing status and connection info.
    """
    moomoo_service = ctx.request_context.lifespan_context.moomoo_service
    status = moomoo_service.check_health()
    
    await ctx.info(f"Health check status: {status.get('status')}")
    
    return status
