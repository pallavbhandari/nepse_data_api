import time
import pytest
from unittest.mock import MagicMock, patch
from nepse_data_api.market import Nepse

class TestNepseMarket:
    
    @patch('nepse_data_api.market.requests.Session')
    def test_market_status(self, mock_session):
        """Test fetching market status"""
        # Setup mock
        mock_instance = mock_session.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isOpen": "OPEN",
            "asOf": "2026-02-15T12:00:00"
        }
        mock_instance.get.return_value = mock_response

        # Test
        with patch('nepse_data_api.market.Nepse.authenticate'):
            nepse = Nepse(enable_cache=False)
            nepse.access_token = "dummy" # Manually set token to avoid auth call
            status = nepse.get_market_status()
            
            assert status['isOpen'] == "OPEN"
            assert status['asOf'] == "2026-02-15T12:00:00"

    @patch('nepse_data_api.market.requests.Session')
    def test_caching(self, mock_session):
        """Test that caching works"""
        mock_instance = mock_session.return_value
        mock_instance.get.return_value.json.return_value = {"data": "test"}
        mock_instance.get.return_value.status_code = 200
        
        with patch.object(Nepse, 'authenticate'):
            nepse = Nepse(enable_cache=True)
            nepse.access_token = "dummy"
            
            # First call - hits API
            nepse.get_market_summary()
            assert mock_instance.get.call_count == 1
            
            # Second call - should hit cache
            nepse.get_market_summary()
            assert mock_instance.get.call_count == 1


class TestTokenFreshness:
    """Each authenticated call should carry a fresh token."""

    def _build(self, **kwargs):
        def fake_auth(self):
            self.access_token = "AUTH"
            self.salts = [1, 2, 3, 4, 5]
            self.token_timestamp = int(time.time())

        def fake_refresh(self):
            self.access_token = "REFRESH"
            self.token_timestamp = int(time.time())
            return {"accessToken": "REFRESH"}

        auth = patch.object(Nepse, "authenticate", autospec=True, side_effect=fake_auth)
        refresh = patch.object(
            Nepse, "refresh_auth_token", autospec=True, side_effect=fake_refresh
        )
        return auth, refresh

    def test_fresh_token_is_reused(self):
        auth, refresh = self._build()
        with auth as m_auth, refresh as m_refresh:
            nepse = Nepse(enable_cache=False, token_validity=10, refresh_validity=100)
            nepse._get_auth_headers()
            assert m_auth.call_count == 1  # only the initial authenticate
            assert m_refresh.call_count == 0

    def test_stale_token_triggers_refresh(self):
        auth, refresh = self._build()
        with auth as m_auth, refresh as m_refresh:
            nepse = Nepse(enable_cache=False, token_validity=10, refresh_validity=100)
            nepse.token_timestamp = int(time.time()) - 20  # past validity
            headers = nepse._get_auth_headers()
            assert m_refresh.call_count == 1
            assert headers["Authorization"] == "Salter REFRESH"

    def test_expired_refresh_token_triggers_reauth(self):
        auth, refresh = self._build()
        with auth as m_auth, refresh as m_refresh:
            nepse = Nepse(enable_cache=False, token_validity=10, refresh_validity=100)
            nepse.token_timestamp = int(time.time()) - 200  # past refresh validity
            headers = nepse._get_auth_headers()
            assert m_refresh.call_count == 0
            assert m_auth.call_count == 2  # initial + full re-auth
            assert headers["Authorization"] == "Salter AUTH"

    def test_zero_validity_refreshes_every_call(self):
        auth, refresh = self._build()
        with auth, refresh as m_refresh:
            nepse = Nepse(enable_cache=False, token_validity=0, refresh_validity=100)
            before = m_refresh.call_count
            nepse._get_auth_headers()
            nepse._get_auth_headers()
            assert m_refresh.call_count - before == 2
