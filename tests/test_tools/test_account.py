"""Unit tests for account tools."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from mcp.shared.context import RequestContext
from mcp.server.fastmcp import Context
from moomoo_mcp.server import AppContext
from moomoo_mcp.services.base_service import MoomooService
from moomoo_mcp.services.trade_service import TradeService
from moomoo_mcp.services.market_data_service import MarketDataService
from moomoo_mcp.tools.account import (
    get_accounts,
    get_account_summary,
    get_assets,
    get_positions,
    get_max_tradable,
    get_margin_ratio,
    get_cash_flow,
    unlock_trade,
)


@pytest.fixture
def mock_trade_service():
    """Create a mock TradeService."""
    return MagicMock(spec=TradeService)


@pytest.fixture
def mock_moomoo_service():
    """Create a mock MoomooService."""
    return MagicMock(spec=MoomooService)


@pytest.fixture
def mock_market_data_service():
    """Create a mock MarketDataService."""
    return MagicMock(spec=MarketDataService)


@pytest.fixture
def app_context(mock_moomoo_service, mock_trade_service, mock_market_data_service):
    """Create AppContext with mock services."""
    return AppContext(
        moomoo_service=mock_moomoo_service,
        trade_service=mock_trade_service,
        market_data_service=mock_market_data_service,
    )


@pytest.fixture
def mcp_context(app_context):
    """Create MCP Context with mocked session."""
    mock_session = MagicMock()
    mock_session.send_log_message = AsyncMock()

    request_context = RequestContext(
        request_id="test-req",
        meta=None,
        session=mock_session,
        lifespan_context=app_context
    )

    mock_fastmcp = MagicMock()
    return Context(request_context=request_context, fastmcp=mock_fastmcp)


@pytest.mark.asyncio
async def test_get_accounts(mcp_context, mock_trade_service):
    """Test get_accounts tool."""
    mock_trade_service.get_accounts.return_value = [
        {"acc_id": 123, "trd_env": "REAL"}
    ]

    result = await get_accounts(mcp_context)

    assert len(result) == 1
    assert result[0]["acc_id"] == 123
    mock_trade_service.get_accounts.assert_called_once()


@pytest.mark.asyncio
async def test_get_assets(mcp_context, mock_trade_service):
    """Test get_assets tool."""
    mock_trade_service.get_assets.return_value = {
        "cash": 10000.0,
        "market_val": 5000.0
    }

    result = await get_assets(mcp_context, trd_env="SIMULATE")

    assert result["cash"] == 10000.0
    mock_trade_service.get_assets.assert_called_once_with(
        trd_env="SIMULATE",
        acc_id=0,
        refresh_cache=False,
        currency=""
    )


@pytest.mark.asyncio
async def test_get_account_summary(mcp_context, mock_trade_service):
    """Test get_account_summary tool."""
    mock_trade_service.get_assets.return_value = {"cash": 10000.0, "market_val": 5000.0}
    mock_trade_service.get_positions.return_value = [{"code": "US.AAPL", "qty": 100}]

    result = await get_account_summary(mcp_context, trd_env="SIMULATE", acc_id=123)

    assert "assets" in result
    assert "positions" in result
    assert result["assets"]["cash"] == 10000.0
    assert len(result["positions"]) == 1
    mock_trade_service.get_assets.assert_called_once_with(trd_env="SIMULATE", acc_id=123)
    mock_trade_service.get_positions.assert_called_once_with(trd_env="SIMULATE", acc_id=123)


@pytest.mark.asyncio
async def test_get_positions(mcp_context, mock_trade_service):
    """Test get_positions tool."""
    mock_trade_service.get_positions.return_value = [
        {"code": "US.AAPL", "qty": 100}
    ]

    result = await get_positions(mcp_context)

    assert len(result) == 1
    assert result[0]["code"] == "US.AAPL"


@pytest.mark.asyncio
async def test_get_max_tradable(mcp_context, mock_trade_service):
    """Test get_max_tradable tool."""
    mock_trade_service.get_max_tradable.return_value = {
        "max_cash_buy": 100
    }

    result = await get_max_tradable(
        mcp_context,
        order_type="NORMAL",
        code="US.AAPL",
        price=150.0
    )

    assert result["max_cash_buy"] == 100
    mock_trade_service.get_max_tradable.assert_called_once()


@pytest.mark.asyncio
async def test_get_margin_ratio(mcp_context, mock_trade_service):
    """Test get_margin_ratio tool."""
    mock_trade_service.get_margin_ratio.return_value = [
        {"code": "US.AAPL", "im_factor": 0.25}
    ]

    result = await get_margin_ratio(mcp_context, code_list=["US.AAPL"])

    assert len(result) == 1
    assert result[0]["im_factor"] == 0.25


@pytest.mark.asyncio
async def test_get_cash_flow(mcp_context, mock_trade_service):
    """Test get_cash_flow tool."""
    mock_trade_service.get_cash_flow.return_value = [
        {"trade_date": "2025-01-01", "amount": 1000.0}
    ]

    result = await get_cash_flow(mcp_context, clearing_date="2025-01-01")

    assert len(result) == 1
    assert result[0]["amount"] == 1000.0


@pytest.mark.asyncio
async def test_unlock_trade(mcp_context, mock_trade_service):
    """Test unlock_trade tool."""
    result = await unlock_trade(mcp_context, password="testpass")

    assert result["status"] == "unlocked"
    mock_trade_service.unlock_trade.assert_called_once_with(
        password="testpass",
        password_md5=None
    )


@pytest.mark.asyncio
async def test_unlock_trade_env_vars(mcp_context, mock_trade_service):
    """Test unlock_trade tool with env vars."""
    import os
    from unittest.mock import patch

    # Use clear=True to remove other env vars like MOOMOO_TRADE_PASSWORD_MD5
    with patch.dict(os.environ, {"MOOMOO_TRADE_PASSWORD": "env_password"}, clear=True):
        result = await unlock_trade(mcp_context)

    assert result["status"] == "unlocked"
    mock_trade_service.unlock_trade.assert_called_once_with(
        password="env_password",
        password_md5=None
    )
