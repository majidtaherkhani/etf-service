"""Shared fixtures and test configuration for ETF tests"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
from io import BytesIO
import pandas as pd

from src.main import app
from src.modules.market_data.models import SecurityPrice
from configs.db.postgresql import get_db


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def mock_market_data_repo(mock_db_session):
    """Mock MarketDataRepository"""
    repo = Mock()
    repo.get_price_history = Mock(return_value=[])
    return repo


@pytest.fixture
def mock_storage_service():
    """Mock StorageService"""
    service = Mock()
    service.upload = AsyncMock(return_value="https://storage.example.com/file.csv")
    return service


@pytest.fixture
def mock_etf_repo(mock_db_session):
    """Mock EtfRepository"""
    repo = Mock()
    repo.log_request = Mock()
    return repo


@pytest.fixture
def sample_price_data():
    """Sample price data for testing"""
    dates = [
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
        datetime(2024, 1, 3),
    ]
    return [
        SecurityPrice(date=dates[0], ticker="AAPL", price=150.0),
        SecurityPrice(date=dates[1], ticker="AAPL", price=151.0),
        SecurityPrice(date=dates[2], ticker="AAPL", price=152.0),
        SecurityPrice(date=dates[0], ticker="MSFT", price=300.0),
        SecurityPrice(date=dates[1], ticker="MSFT", price=301.0),
        SecurityPrice(date=dates[2], ticker="MSFT", price=302.0),
    ]


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing"""
    data = {
        'name': ['AAPL', 'MSFT'],
        'weight': [0.6, 0.4]
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')


@pytest.fixture
def sample_csv_file(sample_csv_content):
    """Sample CSV file for upload"""
    return ("test_portfolio.csv", BytesIO(sample_csv_content), "text/csv")


@pytest.fixture
def client(monkeypatch):
    """Test client for FastAPI app with rate limiting disabled"""
    # Disable rate limiting for tests by mocking the limiter
    from unittest.mock import Mock
    from slowapi import Limiter
    
    # Create a mock limiter that doesn't enforce limits
    mock_limiter = Mock(spec=Limiter)
    mock_limiter.limit = lambda *args, **kwargs: lambda f: f  # Return function unchanged
    
    # Patch the limiter in the app
    monkeypatch.setattr(app.state, "limiter", mock_limiter)
    
    return TestClient(app)


@pytest.fixture
def override_get_db(mock_db_session):
    """Override database dependency"""
    def _get_db():
        yield mock_db_session
    return _get_db
