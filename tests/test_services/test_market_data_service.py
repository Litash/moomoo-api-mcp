"""Unit tests for MarketDataService."""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from moomoo_mcp.services.market_data_service import MarketDataService


@pytest.fixture
def mock_quote_ctx():
    """Create a mock OpenQuoteContext."""
    return MagicMock()


@pytest.fixture
def market_data_service(mock_quote_ctx):
    """Create MarketDataService with mocked context."""
    return MarketDataService(quote_ctx=mock_quote_ctx)


class TestSubscribe:
    """Tests for subscribe method."""

    def test_subscribe_success(self, market_data_service, mock_quote_ctx):
        """Test successful subscription."""
        mock_quote_ctx.subscribe.return_value = (0, None)  # RET_OK = 0

        from moomoo import SubType
        market_data_service.subscribe(["US.AAPL"], [SubType.QUOTE])

        mock_quote_ctx.subscribe.assert_called_once()

    def test_subscribe_error(self, market_data_service, mock_quote_ctx):
        """Test subscription error handling."""
        mock_quote_ctx.subscribe.return_value = (-1, "Subscription failed")

        from moomoo import SubType
        with pytest.raises(RuntimeError, match="subscribe failed"):
            market_data_service.subscribe(["US.AAPL"], [SubType.QUOTE])

    def test_subscribe_no_context(self):
        """Test error when context is None."""
        service = MarketDataService(quote_ctx=None)

        from moomoo import SubType
        with pytest.raises(RuntimeError, match="Quote context not connected"):
            service.subscribe(["US.AAPL"], [SubType.QUOTE])


class TestGetStockQuote:
    """Tests for get_stock_quote method."""

    def test_get_stock_quote_success(self, market_data_service, mock_quote_ctx):
        """Test successful quote retrieval."""
        mock_quote_ctx.subscribe.return_value = (0, None)
        df = pd.DataFrame([{
            "code": "US.AAPL",
            "last_price": 150.0,
            "open_price": 149.0,
            "high_price": 151.0,
            "low_price": 148.0,
            "volume": 1000000,
        }])
        mock_quote_ctx.get_stock_quote.return_value = (0, df)

        result = market_data_service.get_stock_quote(["US.AAPL"])

        assert len(result) == 1
        assert result[0]["code"] == "US.AAPL"
        assert result[0]["last_price"] == 150.0
        mock_quote_ctx.subscribe.assert_called_once()
        mock_quote_ctx.get_stock_quote.assert_called_once_with(["US.AAPL"])

    def test_get_stock_quote_multiple_codes(self, market_data_service, mock_quote_ctx):
        """Test quote retrieval for multiple stocks."""
        mock_quote_ctx.subscribe.return_value = (0, None)
        df = pd.DataFrame([
            {"code": "US.AAPL", "last_price": 150.0},
            {"code": "US.TSLA", "last_price": 250.0},
        ])
        mock_quote_ctx.get_stock_quote.return_value = (0, df)

        result = market_data_service.get_stock_quote(["US.AAPL", "US.TSLA"])

        assert len(result) == 2
        assert result[0]["code"] == "US.AAPL"
        assert result[1]["code"] == "US.TSLA"

    def test_get_stock_quote_error(self, market_data_service, mock_quote_ctx):
        """Test error handling for quote retrieval."""
        mock_quote_ctx.subscribe.return_value = (0, None)
        mock_quote_ctx.get_stock_quote.return_value = (-1, "API Error")

        with pytest.raises(RuntimeError, match="get_stock_quote failed"):
            market_data_service.get_stock_quote(["US.AAPL"])

    def test_get_stock_quote_no_context(self):
        """Test error when context is None."""
        service = MarketDataService(quote_ctx=None)

        with pytest.raises(RuntimeError, match="Quote context not connected"):
            service.get_stock_quote(["US.AAPL"])


class TestGetHistoricalKlines:
    """Tests for get_historical_klines method."""

    def test_get_historical_klines_success(self, market_data_service, mock_quote_ctx):
        """Test successful K-line retrieval."""
        df = pd.DataFrame([
            {"time_key": "2025-01-01 00:00:00", "open": 150.0, "close": 151.0, "high": 152.0, "low": 149.0, "volume": 1000},
            {"time_key": "2025-01-02 00:00:00", "open": 151.0, "close": 152.0, "high": 153.0, "low": 150.0, "volume": 1100},
        ])
        mock_quote_ctx.request_history_kline.return_value = (0, df, None)

        result = market_data_service.get_historical_klines("US.AAPL", ktype="K_DAY")

        assert len(result) == 2
        assert result[0]["open"] == 150.0
        assert result[1]["close"] == 152.0

    def test_get_historical_klines_with_dates(self, market_data_service, mock_quote_ctx):
        """Test K-line retrieval with date range."""
        df = pd.DataFrame([{"time_key": "2025-01-01 00:00:00", "open": 150.0, "close": 151.0}])
        mock_quote_ctx.request_history_kline.return_value = (0, df, None)

        result = market_data_service.get_historical_klines(
            "US.AAPL",
            ktype="K_DAY",
            start="2025-01-01",
            end="2025-01-15",
            max_count=50,
        )

        assert len(result) == 1
        call_kwargs = mock_quote_ctx.request_history_kline.call_args.kwargs
        assert call_kwargs["code"] == "US.AAPL"
        assert call_kwargs["start"] == "2025-01-01"
        assert call_kwargs["end"] == "2025-01-15"
        assert call_kwargs["max_count"] == 50

    def test_get_historical_klines_1m(self, market_data_service, mock_quote_ctx):
        """Test 1-minute K-line retrieval."""
        df = pd.DataFrame([{"time_key": "2025-01-01 09:30:00", "open": 150.0, "close": 150.5}])
        mock_quote_ctx.request_history_kline.return_value = (0, df, None)

        result = market_data_service.get_historical_klines("US.AAPL", ktype="K_1M")

        assert len(result) == 1
        # Verify ktype enum was used correctly
        from moomoo import KLType
        call_kwargs = mock_quote_ctx.request_history_kline.call_args.kwargs
        assert call_kwargs["ktype"] == KLType.K_1M

    def test_get_historical_klines_error(self, market_data_service, mock_quote_ctx):
        """Test error handling for K-line retrieval."""
        mock_quote_ctx.request_history_kline.return_value = (-1, "API Error", None)

        with pytest.raises(RuntimeError, match="request_history_kline failed"):
            market_data_service.get_historical_klines("US.AAPL")

    def test_get_historical_klines_no_context(self):
        """Test error when context is None."""
        service = MarketDataService(quote_ctx=None)

        with pytest.raises(RuntimeError, match="Quote context not connected"):
            service.get_historical_klines("US.AAPL")


class TestGetMarketSnapshot:
    """Tests for get_market_snapshot method."""

    def test_get_market_snapshot_success(self, market_data_service, mock_quote_ctx):
        """Test successful snapshot retrieval."""
        df = pd.DataFrame([
            {"code": "US.AAPL", "last_price": 150.0, "volume": 1000000, "pe_ratio": 25.0},
        ])
        mock_quote_ctx.get_market_snapshot.return_value = (0, df)

        result = market_data_service.get_market_snapshot(["US.AAPL"])

        assert len(result) == 1
        assert result[0]["code"] == "US.AAPL"
        assert result[0]["last_price"] == 150.0
        assert result[0]["pe_ratio"] == 25.0

    def test_get_market_snapshot_multiple(self, market_data_service, mock_quote_ctx):
        """Test snapshot for multiple stocks (watchlist scenario)."""
        df = pd.DataFrame([
            {"code": "US.AAPL", "last_price": 150.0},
            {"code": "US.TSLA", "last_price": 250.0},
            {"code": "US.GOOGL", "last_price": 140.0},
        ])
        mock_quote_ctx.get_market_snapshot.return_value = (0, df)

        result = market_data_service.get_market_snapshot(["US.AAPL", "US.TSLA", "US.GOOGL"])

        assert len(result) == 3

    def test_get_market_snapshot_empty_list(self, market_data_service, mock_quote_ctx):
        """Test snapshot with empty code list returns empty."""
        result = market_data_service.get_market_snapshot([])

        assert result == []
        mock_quote_ctx.get_market_snapshot.assert_not_called()

    def test_get_market_snapshot_error(self, market_data_service, mock_quote_ctx):
        """Test error handling for snapshot retrieval."""
        mock_quote_ctx.get_market_snapshot.return_value = (-1, "API Error")

        with pytest.raises(RuntimeError, match="get_market_snapshot failed"):
            market_data_service.get_market_snapshot(["US.AAPL"])

    def test_get_market_snapshot_no_context(self):
        """Test error when context is None."""
        service = MarketDataService(quote_ctx=None)

        with pytest.raises(RuntimeError, match="Quote context not connected"):
            service.get_market_snapshot(["US.AAPL"])


class TestGetOrderBook:
    """Tests for get_order_book method."""

    def test_get_order_book_success(self, market_data_service, mock_quote_ctx):
        """Test successful order book retrieval."""
        mock_quote_ctx.subscribe.return_value = (0, None)
        order_book_data = {
            "code": "HK.00700",
            "Bid": [(400.0, 1000, 5, {}), (399.8, 2000, 10, {})],
            "Ask": [(400.2, 800, 4, {}), (400.4, 1500, 8, {})],
        }
        mock_quote_ctx.get_order_book.return_value = (0, order_book_data)

        result = market_data_service.get_order_book("HK.00700", num=10)

        assert result["code"] == "HK.00700"
        assert len(result["Bid"]) == 2
        assert len(result["Ask"]) == 2
        assert result["Bid"][0][0] == 400.0  # First bid price
        mock_quote_ctx.subscribe.assert_called_once()

    def test_get_order_book_custom_levels(self, market_data_service, mock_quote_ctx):
        """Test order book with custom number of levels."""
        mock_quote_ctx.subscribe.return_value = (0, None)
        order_book_data = {
            "code": "US.AAPL",
            "Bid": [(150.0, 100, 1, {})],
            "Ask": [(150.1, 200, 2, {})],
        }
        mock_quote_ctx.get_order_book.return_value = (0, order_book_data)

        result = market_data_service.get_order_book("US.AAPL", num=5)

        mock_quote_ctx.get_order_book.assert_called_once_with("US.AAPL", num=5)

    def test_get_order_book_error(self, market_data_service, mock_quote_ctx):
        """Test error handling for order book retrieval."""
        mock_quote_ctx.subscribe.return_value = (0, None)
        mock_quote_ctx.get_order_book.return_value = (-1, "API Error")

        with pytest.raises(RuntimeError, match="get_order_book failed"):
            market_data_service.get_order_book("HK.00700")

    def test_get_order_book_no_context(self):
        """Test error when context is None."""
        service = MarketDataService(quote_ctx=None)

        with pytest.raises(RuntimeError, match="Quote context not connected"):
            service.get_order_book("HK.00700")
