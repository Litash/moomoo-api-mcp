"""Unit tests for TradeService."""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from moomoo_mcp.services.trade_service import TradeService


@pytest.fixture
def mock_trade_ctx():
    """Create a mock OpenSecTradeContext."""
    return MagicMock()


@pytest.fixture
def trade_service_with_mock(mock_trade_ctx):
    """Create TradeService with mocked context."""
    service = TradeService()
    service.trade_ctx = mock_trade_ctx
    return service


class TestTradeServiceConnection:
    """Tests for connection lifecycle."""

    @patch("moomoo_mcp.services.trade_service.OpenSecTradeContext")
    def test_connect_creates_context(self, mock_ctx_class):
        """Test connect() initializes OpenSecTradeContext."""
        service = TradeService(host="localhost", port=12345)
        service.connect()

        mock_ctx_class.assert_called_once_with(host="localhost", port=12345)
        assert service.trade_ctx is not None

    def test_close_clears_context(self, trade_service_with_mock, mock_trade_ctx):
        """Test close() closes and clears trade context."""
        trade_service_with_mock.close()

        mock_trade_ctx.close.assert_called_once()
        assert trade_service_with_mock.trade_ctx is None


class TestGetAccounts:
    """Tests for get_accounts."""

    def test_get_accounts_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful account list retrieval."""
        df = pd.DataFrame([{"acc_id": 123, "trd_env": "REAL"}])
        mock_trade_ctx.get_acc_list.return_value = (0, df)  # RET_OK = 0

        result = trade_service_with_mock.get_accounts()

        assert len(result) == 1
        assert result[0]["acc_id"] == 123
        mock_trade_ctx.get_acc_list.assert_called_once()

    def test_get_accounts_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test error handling for failed account list."""
        mock_trade_ctx.get_acc_list.return_value = (-1, "API Error")

        with pytest.raises(RuntimeError, match="get_acc_list failed"):
            trade_service_with_mock.get_accounts()

    def test_get_accounts_no_context(self):
        """Test error when context not connected."""
        service = TradeService()

        with pytest.raises(RuntimeError, match="Trade context not connected"):
            service.get_accounts()


class TestGetAssets:
    """Tests for get_assets."""

    def test_get_assets_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful assets retrieval."""
        df = pd.DataFrame([{"cash": 10000.0, "market_val": 5000.0}])
        mock_trade_ctx.accinfo_query.return_value = (0, df)

        result = trade_service_with_mock.get_assets(trd_env="SIMULATE")

        assert result["cash"] == 10000.0
        mock_trade_ctx.accinfo_query.assert_called_once()

    def test_get_assets_empty(self, trade_service_with_mock, mock_trade_ctx):
        """Test empty assets result."""
        df = pd.DataFrame([])
        mock_trade_ctx.accinfo_query.return_value = (0, df)

        result = trade_service_with_mock.get_assets()

        assert result == {}


class TestGetPositions:
    """Tests for get_positions."""

    def test_get_positions_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful positions retrieval."""
        df = pd.DataFrame([
            {"code": "US.AAPL", "qty": 100},
            {"code": "US.TSLA", "qty": 50},
        ])
        mock_trade_ctx.position_list_query.return_value = (0, df)

        result = trade_service_with_mock.get_positions()

        assert len(result) == 2
        assert result[0]["code"] == "US.AAPL"

    def test_get_positions_with_code_filter(self, trade_service_with_mock, mock_trade_ctx):
        """Test positions with code filter."""
        df = pd.DataFrame([{"code": "US.AAPL", "qty": 100}])
        mock_trade_ctx.position_list_query.return_value = (0, df)

        result = trade_service_with_mock.get_positions(code="US.AAPL")

        mock_trade_ctx.position_list_query.assert_called_once()
        call_kwargs = mock_trade_ctx.position_list_query.call_args.kwargs
        assert call_kwargs["code"] == "US.AAPL"


class TestGetMaxTradable:
    """Tests for get_max_tradable."""

    def test_get_max_tradable_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test max tradable quantity retrieval."""
        df = pd.DataFrame([{"max_cash_buy": 100, "max_sell_short": 50}])
        mock_trade_ctx.acctradinginfo_query.return_value = (0, df)

        result = trade_service_with_mock.get_max_tradable(
            order_type="NORMAL",
            code="US.AAPL",
            price=150.0
        )

        assert result["max_cash_buy"] == 100
        mock_trade_ctx.acctradinginfo_query.assert_called_once()


class TestGetMarginRatio:
    """Tests for get_margin_ratio."""

    def test_get_margin_ratio_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test margin ratio retrieval."""
        df = pd.DataFrame([{"code": "US.AAPL", "im_factor": 0.25}])
        mock_trade_ctx.get_margin_ratio.return_value = (0, df)

        result = trade_service_with_mock.get_margin_ratio(["US.AAPL"])

        assert len(result) == 1
        assert result[0]["im_factor"] == 0.25


class TestGetCashFlow:
    """Tests for get_cash_flow."""

    def test_get_cash_flow_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test cash flow retrieval."""
        df = pd.DataFrame([{"trade_date": "2025-01-01", "amount": 1000.0}])
        mock_trade_ctx.get_acc_cash_flow.return_value = (0, df)

        result = trade_service_with_mock.get_cash_flow(clearing_date="2025-01-01")

        assert len(result) == 1
        assert result[0]["amount"] == 1000.0


class TestUnlockTrade:
    """Tests for unlock_trade."""

    def test_unlock_trade_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful trade unlock."""
        mock_trade_ctx.unlock_trade.return_value = (0, None)

        trade_service_with_mock.unlock_trade(password="testpass")

        mock_trade_ctx.unlock_trade.assert_called_once_with(
            password="testpass",
            password_md5=None,
            is_unlock=True
        )

    def test_unlock_trade_with_md5(self, trade_service_with_mock, mock_trade_ctx):
        """Test trade unlock with MD5 password."""
        mock_trade_ctx.unlock_trade.return_value = (0, None)

        trade_service_with_mock.unlock_trade(password_md5="abc123")

        mock_trade_ctx.unlock_trade.assert_called_once_with(
            password=None,
            password_md5="abc123",
            is_unlock=True
        )

    def test_unlock_trade_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test unlock trade error handling."""
        mock_trade_ctx.unlock_trade.return_value = (-1, "Invalid password")

        with pytest.raises(RuntimeError, match="unlock_trade failed"):
            trade_service_with_mock.unlock_trade(password="wrongpass")
