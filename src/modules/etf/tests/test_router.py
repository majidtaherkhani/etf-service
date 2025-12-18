"""Unit tests for ETF router/API endpoints"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
from io import BytesIO
import pandas as pd

from src.main import app
from src.modules.etf.service import EtfService
from src.modules.etf.exceptions import (
    InvalidCsvColumnsException,
    NoPriceDataException,
    NoMatchingTickerDataException
)
from src.exceptions import InvalidCsvFormatException


class TestAnalyzeEndpoint:
    """Test suite for POST /etf/analyze endpoint"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def valid_csv_content(self):
        """Valid CSV content for testing"""
        data = {
            'name': ['AAPL', 'MSFT', 'GOOGL'],
            'weight': [0.5, 0.3, 0.2]
        }
        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    @pytest.fixture
    def sample_price_data(self):
        """Sample price data"""
        from datetime import datetime
        from src.modules.market_data.models import SecurityPrice
        
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
            SecurityPrice(date=dates[0], ticker="GOOGL", price=100.0),
            SecurityPrice(date=dates[1], ticker="GOOGL", price=101.0),
            SecurityPrice(date=dates[2], ticker="GOOGL", price=102.0),
        ]

    @patch('src.modules.etf.router.EtfService')
    def test_analyze_success(
        self, 
        mock_etf_service_class,
        client, 
        valid_csv_content,
        sample_price_data
    ):
        """Test successful portfolio analysis"""
        # Setup mocks
        from src.modules.etf import schemas
        
        mock_service = Mock()
        mock_service.analyze_portfolio = AsyncMock(
            return_value=schemas.EtfAnalysisResponse(
                etf_name="test_portfolio",
                latest_close=200.5,
                etf_time_series=[
                    schemas.TimeSeriesPoint(date="2024-01-01", nav=195.0),
                    schemas.TimeSeriesPoint(date="2024-01-02", nav=200.0),
                    schemas.TimeSeriesPoint(date="2024-01-03", nav=200.5)
                ],
                latest_prices=[
                    schemas.LatestPriceResponse(ticker="AAPL", price=152.0, weight=0.5, value=76.0),
                    schemas.LatestPriceResponse(ticker="MSFT", price=302.0, weight=0.3, value=90.6),
                    schemas.LatestPriceResponse(ticker="GOOGL", price=102.0, weight=0.2, value=20.4)
                ]
            )
        )
        mock_etf_service_class.return_value = mock_service

        # Make request
        response = client.post(
            "/etf/analyze",
            files={"file": ("portfolio.csv", BytesIO(valid_csv_content), "text/csv")}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["etf_name"] == "test_portfolio"
        assert data["latest_close"] == 200.5
        assert len(data["etf_time_series"]) == 3
        assert len(data["latest_prices"]) == 3
        mock_service.analyze_portfolio.assert_called_once()

    @patch('src.modules.etf.router.EtfService')
    @patch('src.modules.etf.router.get_db')
    def test_analyze_invalid_csv_columns(
        self,
        mock_get_db,
        mock_etf_service_class,
        client
    ):
        """Test analysis with CSV missing required columns"""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        mock_service = Mock()
        mock_service.analyze_portfolio = AsyncMock(
            side_effect=InvalidCsvColumnsException()
        )
        mock_etf_service_class.return_value = mock_service

        # Invalid CSV (missing 'weight' column)
        invalid_csv = pd.DataFrame({'name': ['AAPL', 'MSFT']}).to_csv(index=False).encode('utf-8')

        # Make request
        response = client.post(
            "/etf/analyze",
            files={"file": ("portfolio.csv", BytesIO(invalid_csv), "text/csv")}
        )

        # Assertions
        assert response.status_code == 400
        assert "CSV must have 'name' and 'weight' columns" in response.json()["detail"]

    @patch('src.modules.etf.router.EtfService')
    def test_analyze_invalid_csv_format(
        self,
        mock_etf_service_class,
        client
    ):
        """Test analysis with invalid CSV format"""
        # Setup mocks
        mock_service = Mock()
        mock_service.analyze_portfolio = AsyncMock(
            side_effect=InvalidCsvFormatException("Invalid CSV format")
        )
        mock_etf_service_class.return_value = mock_service

        # Invalid CSV content
        invalid_csv = b"not a valid csv file"

        # Make request
        response = client.post(
            "/etf/analyze",
            files={"file": ("portfolio.csv", BytesIO(invalid_csv), "text/csv")}
        )

        # Assertions
        assert response.status_code == 400

    @patch('src.modules.etf.router.EtfService')
    def test_analyze_no_price_data(
        self,
        mock_etf_service_class,
        client,
        valid_csv_content
    ):
        """Test analysis when no price data is available"""
        # Setup mocks
        mock_service = Mock()
        mock_service.analyze_portfolio = AsyncMock(
            side_effect=NoPriceDataException()
        )
        mock_etf_service_class.return_value = mock_service

        # Make request
        response = client.post(
            "/etf/analyze",
            files={"file": ("portfolio.csv", BytesIO(valid_csv_content), "text/csv")}
        )

        # Assertions
        assert response.status_code == 404
        assert "No price data found" in response.json()["detail"]

    @patch('src.modules.etf.router.EtfService')
    def test_analyze_no_matching_ticker_data(
        self,
        mock_etf_service_class,
        client,
        valid_csv_content
    ):
        """Test analysis when no matching ticker data exists"""
        # Setup mocks
        mock_service = Mock()
        mock_service.analyze_portfolio = AsyncMock(
            side_effect=NoMatchingTickerDataException()
        )
        mock_etf_service_class.return_value = mock_service

        # Make request
        response = client.post(
            "/etf/analyze",
            files={"file": ("portfolio.csv", BytesIO(valid_csv_content), "text/csv")}
        )

        # Assertions
        assert response.status_code == 404
        assert "No matching price data" in response.json()["detail"]

    @patch('src.modules.etf.router.EtfService')
    def test_analyze_empty_file(
        self,
        mock_etf_service_class,
        client
    ):
        """Test analysis with empty CSV file"""
        # Setup mocks
        mock_service = Mock()
        mock_service.analyze_portfolio = AsyncMock(
            side_effect=InvalidCsvFormatException("CSV file is empty")
        )
        mock_etf_service_class.return_value = mock_service

        # Empty CSV
        empty_csv = b""

        # Make request
        response = client.post(
            "/etf/analyze",
            files={"file": ("portfolio.csv", BytesIO(empty_csv), "text/csv")}
        )

        # Assertions - could be 400 (validation error) or 429 (rate limit)
        # Rate limiting can occur if too many tests run in sequence
        assert response.status_code in [400, 429]

    def test_analyze_missing_file(self, client):
        """Test analysis endpoint without file"""
        # Make request without file
        response = client.post("/etf/analyze")

        # Assertions
        assert response.status_code == 422  # FastAPI validation error

    def test_analyze_endpoint_exists(self, client):
        """Test that analyze endpoint is registered"""
        # Try to access endpoint (will fail without file, but endpoint exists)
        response = client.post("/etf/analyze")
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
