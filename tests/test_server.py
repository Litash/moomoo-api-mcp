"""Tests for auto-unlock trade at startup functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest

from moomoo_mcp.server import _auto_unlock_trade


class TestAutoUnlockTrade:
    """Tests for _auto_unlock_trade function."""

    def test_auto_unlock_with_plain_password(self) -> None:
        """Test auto-unlock when MOOMOO_TRADE_PASSWORD is set."""
        mock_trade_service = MagicMock()
        mock_trade_service.get_accounts.return_value = [{"acc_id": 123}]

        with patch.dict(os.environ, {"MOOMOO_TRADE_PASSWORD": "test_password"}, clear=False):
            _auto_unlock_trade(mock_trade_service)

        # get_accounts must be called first to initialize account context
        mock_trade_service.get_accounts.assert_called_once()
        mock_trade_service.unlock_trade.assert_called_once_with(password="test_password")

    def test_auto_unlock_with_md5_password(self) -> None:
        """Test auto-unlock when only MOOMOO_TRADE_PASSWORD_MD5 is set."""
        mock_trade_service = MagicMock()

        env_vars = {"MOOMOO_TRADE_PASSWORD_MD5": "md5_hash_value"}
        with patch.dict(os.environ, env_vars, clear=False):
            # Ensure plain password is not set
            if "MOOMOO_TRADE_PASSWORD" in os.environ:
                del os.environ["MOOMOO_TRADE_PASSWORD"]
            _auto_unlock_trade(mock_trade_service)

        mock_trade_service.unlock_trade.assert_called_once_with(password_md5="md5_hash_value")

    def test_plain_password_takes_precedence(self) -> None:
        """Test that plain password takes precedence over MD5."""
        mock_trade_service = MagicMock()

        env_vars = {
            "MOOMOO_TRADE_PASSWORD": "plain_password",
            "MOOMOO_TRADE_PASSWORD_MD5": "md5_hash",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            _auto_unlock_trade(mock_trade_service)

        # Should use plain password, not MD5
        mock_trade_service.unlock_trade.assert_called_once_with(password="plain_password")

    def test_skip_unlock_when_no_env_vars(self) -> None:
        """Test that unlock is skipped when no env vars are set."""
        mock_trade_service = MagicMock()

        # Create a clean environment without the password vars
        clean_env = {k: v for k, v in os.environ.items() 
                     if k not in ("MOOMOO_TRADE_PASSWORD", "MOOMOO_TRADE_PASSWORD_MD5")}
        
        with patch.dict(os.environ, clean_env, clear=True):
            _auto_unlock_trade(mock_trade_service)

        mock_trade_service.unlock_trade.assert_not_called()

    def test_graceful_failure_on_unlock_error(self) -> None:
        """Test that unlock failure is handled gracefully (no exception raised)."""
        mock_trade_service = MagicMock()
        mock_trade_service.unlock_trade.side_effect = RuntimeError("Invalid password")

        with patch.dict(os.environ, {"MOOMOO_TRADE_PASSWORD": "wrong_password"}, clear=False):
            # Should not raise an exception
            _auto_unlock_trade(mock_trade_service)

        mock_trade_service.unlock_trade.assert_called_once()
