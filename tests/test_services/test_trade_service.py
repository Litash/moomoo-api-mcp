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
        df = pd.DataFrame(
            [
                {"code": "US.AAPL", "qty": 100},
                {"code": "US.TSLA", "qty": 50},
            ]
        )
        mock_trade_ctx.position_list_query.return_value = (0, df)

        result = trade_service_with_mock.get_positions()

        assert len(result) == 2
        assert result[0]["code"] == "US.AAPL"

    def test_get_positions_with_code_filter(
        self, trade_service_with_mock, mock_trade_ctx
    ):
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
            order_type="NORMAL", code="US.AAPL", price=150.0
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
            password="testpass", password_md5=None, is_unlock=True
        )

    def test_unlock_trade_with_md5(self, trade_service_with_mock, mock_trade_ctx):
        """Test trade unlock with MD5 password."""
        mock_trade_ctx.unlock_trade.return_value = (0, None)

        trade_service_with_mock.unlock_trade(password_md5="abc123")

        mock_trade_ctx.unlock_trade.assert_called_once_with(
            password=None, password_md5="abc123", is_unlock=True
        )

    def test_unlock_trade_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test unlock trade error handling."""
        mock_trade_ctx.unlock_trade.return_value = (-1, "Invalid password")

        with pytest.raises(RuntimeError, match="unlock_trade failed"):
            trade_service_with_mock.unlock_trade(password="wrongpass")


class TestPlaceOrder:
    """Tests for place_order."""

    def test_place_order_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful order placement."""
        df = pd.DataFrame(
            [
                {
                    "order_id": "123456",
                    "order_status": "SUBMITTED",
                    "code": "US.AAPL",
                    "qty": 100,
                    "price": 150.0,
                }
            ]
        )
        mock_trade_ctx.place_order.return_value = (0, df)

        result = trade_service_with_mock.place_order(
            code="US.AAPL",
            price=150.0,
            qty=100,
            trd_side="BUY",
            order_type="NORMAL",
            trd_env="SIMULATE",
            acc_id=123,
        )

        assert result["order_id"] == "123456"
        mock_trade_ctx.place_order.assert_called_once()

    def test_place_order_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test order placement failure."""
        mock_trade_ctx.place_order.return_value = (-1, "Order rejected")

        with pytest.raises(RuntimeError, match="place_order failed"):
            trade_service_with_mock.place_order(
                code="US.AAPL",
                price=150.0,
                qty=100,
                trd_side="BUY",
            )

    def test_place_order_no_context(self):
        """Test error when context not connected."""
        service = TradeService()

        with pytest.raises(RuntimeError, match="Trade context not connected"):
            service.place_order(
                code="US.AAPL",
                price=150.0,
                qty=100,
                trd_side="BUY",
            )

    def test_place_order_with_time_in_force_gtc(
        self, trade_service_with_mock, mock_trade_ctx
    ):
        """Test order placement with GTC time in force."""
        df = pd.DataFrame(
            [
                {
                    "order_id": "123456",
                    "order_status": "SUBMITTED",
                    "code": "US.AAPL",
                    "qty": 100,
                    "price": 150.0,
                    "time_in_force": "GTC",
                }
            ]
        )
        mock_trade_ctx.place_order.return_value = (0, df)

        result = trade_service_with_mock.place_order(
            code="US.AAPL",
            price=150.0,
            qty=100,
            trd_side="BUY",
            order_type="NORMAL",
            time_in_force="GTC",
            trd_env="SIMULATE",
            acc_id=123,
        )

        assert result["order_id"] == "123456"
        mock_trade_ctx.place_order.assert_called_once()
        call_kwargs = mock_trade_ctx.place_order.call_args.kwargs
        assert call_kwargs["time_in_force"] == "GTC"

    def test_place_order_with_time_in_force_day(
        self, trade_service_with_mock, mock_trade_ctx
    ):
        """Test order placement with DAY time in force (default)."""
        df = pd.DataFrame(
            [
                {
                    "order_id": "123456",
                    "order_status": "SUBMITTED",
                    "code": "US.AAPL",
                    "qty": 100,
                    "price": 150.0,
                    "time_in_force": "DAY",
                }
            ]
        )
        mock_trade_ctx.place_order.return_value = (0, df)

        result = trade_service_with_mock.place_order(
            code="US.AAPL",
            price=150.0,
            qty=100,
            trd_side="BUY",
            order_type="NORMAL",
            trd_env="SIMULATE",
            acc_id=123,
        )

        assert result["order_id"] == "123456"
        mock_trade_ctx.place_order.assert_called_once()
        call_kwargs = mock_trade_ctx.place_order.call_args.kwargs
        # Default should be DAY
        assert call_kwargs["time_in_force"] == "DAY"

    def test_place_order_with_special_limit_order_type(
        self, trade_service_with_mock, mock_trade_ctx
    ):
        """Test order placement with SPECIAL_LIMIT order type."""
        df = pd.DataFrame(
            [
                {
                    "order_id": "123456",
                    "order_status": "SUBMITTED",
                    "code": "HK.00700",
                    "qty": 100,
                    "price": 300.0,
                }
            ]
        )
        mock_trade_ctx.place_order.return_value = (0, df)

        result = trade_service_with_mock.place_order(
            code="HK.00700",
            price=300.0,
            qty=100,
            trd_side="BUY",
            order_type="SPECIAL_LIMIT",
            time_in_force="DAY",
            trd_env="SIMULATE",
            acc_id=123,
        )

        assert result["order_id"] == "123456"
        call_kwargs = mock_trade_ctx.place_order.call_args.kwargs
        assert call_kwargs["order_type"] == "SPECIAL_LIMIT"


class TestModifyOrder:
    """Tests for modify_order."""

    def test_modify_order_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful order modification."""
        df = pd.DataFrame(
            [
                {
                    "order_id": "123456",
                    "order_status": "MODIFIED",
                }
            ]
        )
        mock_trade_ctx.modify_order.return_value = (0, df)

        result = trade_service_with_mock.modify_order(
            order_id="123456",
            modify_order_op="NORMAL",
            qty=200,
            price=155.0,
            trd_env="SIMULATE",
            acc_id=123,
        )

        assert result["order_status"] == "MODIFIED"
        mock_trade_ctx.modify_order.assert_called_once()

    def test_modify_order_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test order modification failure."""
        mock_trade_ctx.modify_order.return_value = (-1, "Modification failed")

        with pytest.raises(RuntimeError, match="modify_order failed"):
            trade_service_with_mock.modify_order(
                order_id="123456",
                modify_order_op="NORMAL",
            )


class TestCancelOrder:
    """Tests for cancel_order."""

    def test_cancel_order_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful order cancellation."""
        df = pd.DataFrame(
            [
                {
                    "order_id": "123456",
                    "order_status": "CANCELLED",
                }
            ]
        )
        mock_trade_ctx.modify_order.return_value = (0, df)

        result = trade_service_with_mock.cancel_order(
            order_id="123456",
            trd_env="SIMULATE",
            acc_id=123,
        )

        assert result["order_status"] == "CANCELLED"
        # Verify CANCEL operation is passed
        call_kwargs = mock_trade_ctx.modify_order.call_args.kwargs
        assert call_kwargs["modify_order_op"] == "CANCEL"
        assert call_kwargs["qty"] == 0
        assert call_kwargs["price"] == 0

    def test_cancel_order_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test order cancellation failure."""
        mock_trade_ctx.modify_order.return_value = (-1, "Cancel failed")

        with pytest.raises(RuntimeError, match="cancel_order failed"):
            trade_service_with_mock.cancel_order(order_id="123456")


class TestGetOrders:
    """Tests for get_orders."""

    def test_get_orders_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful order list retrieval."""
        df = pd.DataFrame(
            [
                {
                    "order_id": "123",
                    "code": "US.AAPL",
                    "qty": 100,
                    "order_status": "SUBMITTED",
                },
                {
                    "order_id": "456",
                    "code": "US.TSLA",
                    "qty": 50,
                    "order_status": "FILLED",
                },
            ]
        )
        mock_trade_ctx.order_list_query.return_value = (0, df)

        result = trade_service_with_mock.get_orders(trd_env="SIMULATE", acc_id=123)

        assert len(result) == 2
        assert result[0]["order_id"] == "123"

    def test_get_orders_with_code_filter(self, trade_service_with_mock, mock_trade_ctx):
        """Test order list with code filter."""
        df = pd.DataFrame([{"order_id": "123", "code": "US.AAPL"}])
        mock_trade_ctx.order_list_query.return_value = (0, df)

        trade_service_with_mock.get_orders(code="US.AAPL")

        call_kwargs = mock_trade_ctx.order_list_query.call_args.kwargs
        assert call_kwargs["code"] == "US.AAPL"

    def test_get_orders_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test order list retrieval failure."""
        mock_trade_ctx.order_list_query.return_value = (-1, "Query failed")

        with pytest.raises(RuntimeError, match="order_list_query failed"):
            trade_service_with_mock.get_orders()


class TestGetDeals:
    """Tests for get_deals."""

    def test_get_deals_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful deal list retrieval."""
        df = pd.DataFrame(
            [
                {"deal_id": "D123", "code": "US.AAPL", "qty": 100, "price": 150.0},
            ]
        )
        mock_trade_ctx.deal_list_query.return_value = (0, df)

        result = trade_service_with_mock.get_deals(trd_env="SIMULATE", acc_id=123)

        assert len(result) == 1
        assert result[0]["deal_id"] == "D123"

    def test_get_deals_with_code_filter(self, trade_service_with_mock, mock_trade_ctx):
        """Test deal list with code filter."""
        df = pd.DataFrame([{"deal_id": "D123", "code": "US.AAPL"}])
        mock_trade_ctx.deal_list_query.return_value = (0, df)

        trade_service_with_mock.get_deals(code="US.AAPL")

        call_kwargs = mock_trade_ctx.deal_list_query.call_args.kwargs
        assert call_kwargs["code"] == "US.AAPL"

    def test_get_deals_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test deal list retrieval failure."""
        mock_trade_ctx.deal_list_query.return_value = (-1, "Query failed")

        with pytest.raises(RuntimeError, match="deal_list_query failed"):
            trade_service_with_mock.get_deals()


class TestGetHistoryOrders:
    """Tests for get_history_orders."""

    def test_get_history_orders_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful history order retrieval."""
        df = pd.DataFrame(
            [
                {"order_id": "H123", "code": "US.AAPL", "order_status": "FILLED"},
            ]
        )
        mock_trade_ctx.history_order_list_query.return_value = (0, df)

        result = trade_service_with_mock.get_history_orders(
            trd_env="SIMULATE",
            acc_id=123,
            start="2025-01-01",
            end="2025-01-15",
        )

        assert len(result) == 1
        assert result[0]["order_id"] == "H123"

    def test_get_history_orders_with_filters(
        self, trade_service_with_mock, mock_trade_ctx
    ):
        """Test history orders with code and status filters."""
        df = pd.DataFrame([])
        mock_trade_ctx.history_order_list_query.return_value = (0, df)

        trade_service_with_mock.get_history_orders(
            code="US.AAPL",
            status_filter_list=["FILLED_ALL"],
        )

        call_kwargs = mock_trade_ctx.history_order_list_query.call_args.kwargs
        assert call_kwargs["code"] == "US.AAPL"
        assert call_kwargs["status_filter_list"] == ["FILLED_ALL"]

    def test_get_history_orders_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test history order retrieval failure."""
        mock_trade_ctx.history_order_list_query.return_value = (-1, "Query failed")

        with pytest.raises(RuntimeError, match="history_order_list_query failed"):
            trade_service_with_mock.get_history_orders()


class TestGetHistoryDeals:
    """Tests for get_history_deals."""

    def test_get_history_deals_success(self, trade_service_with_mock, mock_trade_ctx):
        """Test successful history deal retrieval."""
        df = pd.DataFrame(
            [
                {"deal_id": "HD123", "code": "US.AAPL", "qty": 100, "price": 150.0},
            ]
        )
        mock_trade_ctx.history_deal_list_query.return_value = (0, df)

        result = trade_service_with_mock.get_history_deals(
            trd_env="SIMULATE",
            acc_id=123,
            start="2025-01-01",
            end="2025-01-15",
        )

        assert len(result) == 1
        assert result[0]["deal_id"] == "HD123"

    def test_get_history_deals_with_code_filter(
        self, trade_service_with_mock, mock_trade_ctx
    ):
        """Test history deals with code filter."""
        df = pd.DataFrame([])
        mock_trade_ctx.history_deal_list_query.return_value = (0, df)

        trade_service_with_mock.get_history_deals(code="US.AAPL")

        call_kwargs = mock_trade_ctx.history_deal_list_query.call_args.kwargs
        assert call_kwargs["code"] == "US.AAPL"

    def test_get_history_deals_error(self, trade_service_with_mock, mock_trade_ctx):
        """Test history deal retrieval failure."""
        mock_trade_ctx.history_deal_list_query.return_value = (-1, "Query failed")

        with pytest.raises(RuntimeError, match="history_deal_list_query failed"):
            trade_service_with_mock.get_history_deals()
