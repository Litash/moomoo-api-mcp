import pytest
from unittest.mock import MagicMock, patch
from moomoo_mcp.services.trade_service import TradeService

@pytest.fixture
def trade_service():
    service = TradeService()
    service.trade_ctx = MagicMock()
    return service

def test_get_market_from_code(trade_service):
    assert trade_service._get_market_from_code("US.AAPL") == "US"
    assert trade_service._get_market_from_code("JP.8058") == "JP"
    assert trade_service._get_market_from_code("HK.00700") == "HK"
    assert trade_service._get_market_from_code("INVALID") is None

def test_find_best_account_success(trade_service):
    mock_accounts = [
        {"acc_id": 1, "trd_env": "SIMULATE", "trdmarket_auth": ["HK", "US"]},
        {"acc_id": 2, "trd_env": "SIMULATE", "trdmarket_auth": ["JP"]},
        {"acc_id": 3, "trd_env": "REAL", "trdmarket_auth": ["JP"]},
    ]
    with patch.object(trade_service, "get_accounts", return_value=mock_accounts):
        # Case 1: Find JP account in SIMULATE
        acc_id = trade_service._find_best_account("SIMULATE", "JP")
        assert acc_id == 2

        # Case 2: Find US account in SIMULATE
        acc_id = trade_service._find_best_account("SIMULATE", "US")
        assert acc_id == 1

        # Case 3: Find JP account in REAL
        acc_id = trade_service._find_best_account("REAL", "JP")
        assert acc_id == 3

def test_find_best_account_failure(trade_service):
    mock_accounts = [
        {"acc_id": 1, "trd_env": "SIMULATE", "trdmarket_auth": ["HK"]},
    ]
    with patch.object(trade_service, "get_accounts", return_value=mock_accounts):
        # Case 1: JP not supported
        with pytest.raises(ValueError, match="No account found in SIMULATE environment that supports trading in JP"):
            trade_service._find_best_account("SIMULATE", "JP")

def test_find_best_account_api_failure(trade_service):
    """Test that API failures raise ValueError instead of silently returning 0."""
    with patch.object(trade_service, "get_accounts", side_effect=RuntimeError("API error")):
        with pytest.raises(ValueError, match="Failed to retrieve account list from the API"):
            trade_service._find_best_account("SIMULATE", "JP")

def test_find_best_account_no_accounts_for_env(trade_service):
    """Test that missing accounts for environment raises ValueError."""
    mock_accounts = [
        {"acc_id": 1, "trd_env": "REAL", "trdmarket_auth": ["JP"]},
    ]
    with patch.object(trade_service, "get_accounts", return_value=mock_accounts):
        with pytest.raises(ValueError, match="No accounts found for the 'SIMULATE' environment"):
            trade_service._find_best_account("SIMULATE", "JP")

def test_place_order_auto_select_account(trade_service):
    mock_accounts = [
        {"acc_id": 999, "trd_env": "SIMULATE", "trdmarket_auth": ["JP"]},
    ]
    
    # Mock place_order return
    trade_service.trade_ctx.place_order.return_value = (0, MagicMock())
    
    with patch.object(trade_service, "get_accounts", return_value=mock_accounts):
        # Call place_order with default acc_id=0
        trade_service.place_order(
            code="JP.8058",
            price=1000,
            qty=100,
            trd_side="BUY",
            trd_env="SIMULATE",
            acc_id=0
        )
        
        # Verify that get_accounts was called to find the account
        # And place_order was called with the CORRECT acc_id (999), not 0
        kwargs = trade_service.trade_ctx.place_order.call_args[1]
        assert kwargs["acc_id"] == 999
        assert kwargs["code"] == "JP.8058"
