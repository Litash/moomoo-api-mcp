"""Unit tests for market data tools."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from mcp.shared.context import RequestContext
from mcp.server.fastmcp import Context
from moomoo_mcp.server import AppContext
from moomoo_mcp.services.base_service import MoomooService
from moomoo_mcp.services.trade_service import TradeService
from moomoo_mcp.services.market_data_service import MarketDataService
from moomoo_mcp.tools.market_data import (
    get_stock_quote,
    get_historical_klines,
    get_market_snapshot,
    get_order_book,
)


@pytest.fixture
def mock_market_data_service():
    """Create a mock MarketDataService."""
    return MagicMock(spec=MarketDataService)


@pytest.fixture
def mock_trade_service():
    """Create a mock TradeService."""
    return MagicMock(spec=TradeService)


@pytest.fixture
def mock_moomoo_service():
    """Create a mock MoomooService."""
    return MagicMock(spec=MoomooService)


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
        lifespan_context=app_context,
    )

    mock_fastmcp = MagicMock()
    return Context(request_context=request_context, fastmcp=mock_fastmcp)


@pytest.mark.asyncio
async def test_get_stock_quote(mcp_context, mock_market_data_service):
    """Test get_stock_quote tool."""
    mock_market_data_service.get_stock_quote.return_value = [
        {"code": "US.AAPL", "last_price": 150.0, "volume": 1000000}
    ]

    result = await get_stock_quote(mcp_context, codes=["US.AAPL"])

    assert len(result) == 1
    assert result[0]["code"] == "US.AAPL"
    assert result[0]["last_price"] == 150.0
    mock_market_data_service.get_stock_quote.assert_called_once_with(["US.AAPL"])


@pytest.mark.asyncio
async def test_get_stock_quote_multiple(mcp_context, mock_market_data_service):
    """Test get_stock_quote with multiple codes."""
    mock_market_data_service.get_stock_quote.return_value = [
        {"code": "US.AAPL", "last_price": 150.0},
        {"code": "US.TSLA", "last_price": 250.0},
    ]

    result = await get_stock_quote(mcp_context, codes=["US.AAPL", "US.TSLA"])

    assert len(result) == 2
    mock_market_data_service.get_stock_quote.assert_called_once_with(["US.AAPL", "US.TSLA"])


@pytest.mark.asyncio
async def test_get_historical_klines(mcp_context, mock_market_data_service):
    """Test get_historical_klines tool."""
    mock_market_data_service.get_historical_klines.return_value = [
        {"time_key": "2025-01-01", "open": 150.0, "close": 151.0, "high": 152.0, "low": 149.0}
    ]

    result = await get_historical_klines(mcp_context, code="US.AAPL")

    assert len(result) == 1
    assert result[0]["open"] == 150.0
    mock_market_data_service.get_historical_klines.assert_called_once_with(
        code="US.AAPL",
        ktype="K_DAY",
        start=None,
        end=None,
        max_count=100,
        autype="QFQ",
    )


@pytest.mark.asyncio
async def test_get_historical_klines_with_params(mcp_context, mock_market_data_service):
    """Test get_historical_klines with custom parameters."""
    mock_market_data_service.get_historical_klines.return_value = []

    await get_historical_klines(
        mcp_context,
        code="US.TSLA",
        ktype="K_1M",
        start="2025-01-01",
        end="2025-01-15",
        max_count=50,
        autype="HFQ",
    )

    mock_market_data_service.get_historical_klines.assert_called_once_with(
        code="US.TSLA",
        ktype="K_1M",
        start="2025-01-01",
        end="2025-01-15",
        max_count=50,
        autype="HFQ",
    )


@pytest.mark.asyncio
async def test_get_market_snapshot(mcp_context, mock_market_data_service):
    """Test get_market_snapshot tool."""
    mock_market_data_service.get_market_snapshot.return_value = [
        {"code": "US.AAPL", "last_price": 150.0, "pe_ratio": 25.0}
    ]

    result = await get_market_snapshot(mcp_context, codes=["US.AAPL"])

    assert len(result) == 1
    assert result[0]["code"] == "US.AAPL"
    mock_market_data_service.get_market_snapshot.assert_called_once_with(["US.AAPL"])


@pytest.mark.asyncio
async def test_get_market_snapshot_watchlist(mcp_context, mock_market_data_service):
    """Test get_market_snapshot with multiple stocks (watchlist scenario)."""
    mock_market_data_service.get_market_snapshot.return_value = [
        {"code": "US.AAPL", "last_price": 150.0},
        {"code": "US.TSLA", "last_price": 250.0},
        {"code": "HK.00700", "last_price": 400.0},
    ]

    result = await get_market_snapshot(
        mcp_context,
        codes=["US.AAPL", "US.TSLA", "HK.00700"],
    )

    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_order_book(mcp_context, mock_market_data_service):
    """Test get_order_book tool."""
    mock_market_data_service.get_order_book.return_value = {
        "code": "HK.00700",
        "Bid": [(400.0, 1000, 5, {})],
        "Ask": [(400.2, 800, 4, {})],
    }

    result = await get_order_book(mcp_context, code="HK.00700")

    assert result["code"] == "HK.00700"
    assert len(result["Bid"]) == 1
    assert len(result["Ask"]) == 1
    mock_market_data_service.get_order_book.assert_called_once_with("HK.00700", num=10)


@pytest.mark.asyncio
async def test_get_order_book_custom_levels(mcp_context, mock_market_data_service):
    """Test get_order_book with custom number of levels."""
    mock_market_data_service.get_order_book.return_value = {
        "code": "US.AAPL",
        "Bid": [],
        "Ask": [],
    }

    await get_order_book(mcp_context, code="US.AAPL", num=5)

    mock_market_data_service.get_order_book.assert_called_once_with("US.AAPL", num=5)
