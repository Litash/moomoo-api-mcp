import pytest
from unittest.mock import MagicMock, AsyncMock
from mcp.shared.context import RequestContext
from mcp.server.fastmcp import Context
from moomoo_mcp.server import AppContext
from moomoo_mcp.tools.system import check_health

@pytest.mark.asyncio
async def test_check_health():
    """Test health check tool returns connected status."""
    
    # Mock MoomooService
    mock_service = MagicMock()
    mock_service.check_health.return_value = {"status": "connected", "host": "127.0.0.1:11111"}
    
    # Create AppContext with mock service
    mock_trade_service = MagicMock()
    mock_market_data_service = MagicMock()
    app_context = AppContext(moomoo_service=mock_service, trade_service=mock_trade_service, market_data_service=mock_market_data_service)
    
    # Mock Session and RequestContext
    mock_session = MagicMock()
    request_context = RequestContext(
        request_id="test-req-1",
        meta=None,
        session=mock_session,
        lifespan_context=app_context
    )
    
    # Mock FastMCP (for logging)
    mock_fastmcp = MagicMock()
    # ctx.info calls ctx.session.send_log_message usually, or fastmcp helpers?
    # Context.info implementation: await self.session.send_log_message(...)
    # So we need mock_session.send_log_message to be async
    mock_session.send_log_message = AsyncMock()
    
    ctx = Context(request_context=request_context, fastmcp=mock_fastmcp)
    
    # Run tool
    result = await check_health(ctx)
    
    # Assertions
    assert result["status"] == "connected"
    mock_service.check_health.assert_called_once()
    mock_session.send_log_message.assert_called()

@pytest.mark.asyncio
async def test_check_health_disconnected():
    """Test health check handles disconnection."""
    
    mock_service = MagicMock()
    mock_service.check_health.return_value = {"status": "disconnected", "error": "Mock error"}
    
    mock_trade_service = MagicMock()
    mock_market_data_service = MagicMock()
    app_context = AppContext(moomoo_service=mock_service, trade_service=mock_trade_service, market_data_service=mock_market_data_service)
    
    mock_session = MagicMock()
    mock_session.send_log_message = AsyncMock()
    
    request_context = RequestContext(
        request_id="test-req-2",
        meta=None,
        session=mock_session,
        lifespan_context=app_context
    )
    
    mock_fastmcp = MagicMock()
    ctx = Context(request_context=request_context, fastmcp=mock_fastmcp)
    
    result = await check_health(ctx)
    
    assert result["status"] == "disconnected"
    assert result["error"] == "Mock error"
