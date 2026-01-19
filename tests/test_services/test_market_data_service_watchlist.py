"""Unit tests for watchlist (user security) methods in MarketDataService."""

import pytest
from unittest.mock import MagicMock
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


class TestGetUserSecurityGroup:
    """Tests for get_user_security_group method."""

    def test_get_user_security_group_success(self, market_data_service, mock_quote_ctx):
        """Test successful retrieval of security groups."""
        df = pd.DataFrame([
            {"group_name": "Favorites", "group_id": 1},
            {"group_name": "Tech", "group_id": 2},
        ])
        mock_quote_ctx.get_user_security_group.return_value = (0, df)

        result = market_data_service.get_user_security_group()

        assert len(result) == 2
        assert result[0]["group_name"] == "Favorites"
        assert result[1]["group_name"] == "Tech"

    def test_get_user_security_group_custom_only(
        self, market_data_service, mock_quote_ctx
    ):
        """Test retrieval of custom groups only."""
        df = pd.DataFrame([{"group_name": "MyList", "group_id": 10}])
        mock_quote_ctx.get_user_security_group.return_value = (0, df)

        result = market_data_service.get_user_security_group(group_type=1)

        assert len(result) == 1
        from moomoo import UserSecurityGroupType
        call_kwargs = mock_quote_ctx.get_user_security_group.call_args.kwargs
        assert call_kwargs["group_type"] == UserSecurityGroupType.CUSTOM

    def test_get_user_security_group_error(self, market_data_service, mock_quote_ctx):
        """Test error handling for security group retrieval."""
        mock_quote_ctx.get_user_security_group.return_value = (-1, "API Error")

        with pytest.raises(RuntimeError, match="get_user_security_group failed"):
            market_data_service.get_user_security_group()

    def test_get_user_security_group_no_context(self):
        """Test error when context is None."""
        service = MarketDataService(quote_ctx=None)

        with pytest.raises(RuntimeError, match="Quote context not connected"):
            service.get_user_security_group()


class TestGetUserSecurity:
    """Tests for get_user_security method."""

    def test_get_user_security_success(self, market_data_service, mock_quote_ctx):
        """Test successful retrieval of securities in a group."""
        df = pd.DataFrame([
            {"code": "US.AAPL", "name": "Apple Inc", "lot_size": 1},
            {"code": "US.NVDA", "name": "NVIDIA Corp", "lot_size": 1},
        ])
        mock_quote_ctx.get_user_security.return_value = (0, df)

        result = market_data_service.get_user_security("Favorites")

        assert len(result) == 2
        assert result[0]["code"] == "US.AAPL"
        assert result[1]["code"] == "US.NVDA"
        mock_quote_ctx.get_user_security.assert_called_once_with("Favorites")

    def test_get_user_security_empty_group(self, market_data_service, mock_quote_ctx):
        """Test retrieval of an empty group."""
        df = pd.DataFrame(columns=["code", "name", "lot_size"])
        mock_quote_ctx.get_user_security.return_value = (0, df)

        result = market_data_service.get_user_security("EmptyGroup")

        assert result == []

    def test_get_user_security_error(self, market_data_service, mock_quote_ctx):
        """Test error handling for security retrieval."""
        mock_quote_ctx.get_user_security.return_value = (-1, "Group not found")

        with pytest.raises(RuntimeError, match="get_user_security failed"):
            market_data_service.get_user_security("NonExistent")

    def test_get_user_security_no_context(self):
        """Test error when context is None."""
        service = MarketDataService(quote_ctx=None)

        with pytest.raises(RuntimeError, match="Quote context not connected"):
            service.get_user_security("Favorites")
