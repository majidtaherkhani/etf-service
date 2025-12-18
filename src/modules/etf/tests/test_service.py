"""Unit tests for ETF service layer"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import UploadFile
from io import BytesIO
import pandas as pd
from datetime import datetime

from src.modules.etf.service import EtfService
from src.modules.etf.exceptions import (
    InvalidCsvColumnsException,
    NoPriceDataException,
    NoMatchingTickerDataException
)
from src.exceptions import InvalidCsvFormatException
from src.modules.market_data.models import SecurityPrice


class TestEtfService:
    """Test suite for EtfService"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()

    @pytest.fixture
    def mock_market_data_repo(self):
        """Mock MarketDataRepository"""
        repo = Mock()
        repo.get_price_history = Mock(return_value=[])
        return repo

    @pytest.fixture
    def mock_storage_service(self):
        """Mock StorageService"""
        service = Mock()
        service.upload = AsyncMock(return_value="https://storage.example.com/file.csv")
        return service

    @pytest.fixture
    def mock_etf_repo(self):
        """Mock EtfRepository"""
        repo = Mock()
        repo.log_request = Mock()
        return repo

    @pytest.fixture
    def service(self, mock_db, mock_market_data_repo, mock_storage_service, mock_etf_repo):
        """Create EtfService instance with mocked dependencies"""
        with patch('src.modules.etf.service.MarketDataRepository') as mock_market_repo_class, \
             patch('src.modules.etf.service.StorageService') as mock_storage_class, \
             patch('src.modules.etf.service.EtfRepository') as mock_etf_repo_class:
            mock_market_repo_class.return_value = mock_market_data_repo
            mock_storage_class.return_value = mock_storage_service
            mock_etf_repo_class.return_value = mock_etf_repo
            service = EtfService(mock_db)
            yield service

    @pytest.fixture
    def valid_csv_content(self):
        """Valid CSV content"""
        data = {
            'name': ['AAPL', 'MSFT'],
            'weight': [0.6, 0.4]
        }
        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    @pytest.fixture
    def sample_price_data(self):
        """Sample price data"""
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

    @pytest.mark.asyncio
    async def test_analyze_portfolio_success(
        self,
        service,
        mock_market_data_repo,
        valid_csv_content,
        sample_price_data
    ):
        """Test successful portfolio analysis"""
        # Setup
        file = UploadFile(
            filename="test_portfolio.csv",
            file=BytesIO(valid_csv_content)
        )
        # Mock the async to_thread calls
        call_count = [0]  # Use list to allow modification in nested function
        async def mock_to_thread(func, *args, **kwargs):
            call_count[0] += 1
            # First call is get_price_history, second is _calculate_portfolio_math
            if call_count[0] == 1:
                return sample_price_data
            elif call_count[0] == 2:
                # Call the actual calculation method
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=sample_price_data)

            # Execute
            result = await service.analyze_portfolio(file)

            # Assertions
            assert result.etf_name == "test_portfolio"
            assert result.latest_close > 0
            assert len(result.etf_time_series) == 3
            assert len(result.latest_prices) == 2
            assert all(ticker in ["AAPL", "MSFT"] for ticker in [p.ticker for p in result.latest_prices])

    @pytest.mark.asyncio
    async def test_analyze_portfolio_invalid_csv_columns(
        self,
        service,
        valid_csv_content
    ):
        """Test analysis with invalid CSV columns"""
        # Setup - CSV missing 'weight' column
        invalid_data = pd.DataFrame({'name': ['AAPL', 'MSFT']})
        invalid_csv = invalid_data.to_csv(index=False).encode('utf-8')
        file = UploadFile(
            filename="test.csv",
            file=BytesIO(invalid_csv)
        )

        # Execute & Assert
        with pytest.raises(InvalidCsvColumnsException):
            await service.analyze_portfolio(file)

    @pytest.mark.asyncio
    async def test_analyze_portfolio_empty_csv(
        self,
        service
    ):
        """Test analysis with empty CSV"""
        # Setup
        empty_csv = b""
        file = UploadFile(
            filename="empty.csv",
            file=BytesIO(empty_csv)
        )

        # Execute & Assert
        with pytest.raises(InvalidCsvFormatException):
            await service.analyze_portfolio(file)

    @pytest.mark.asyncio
    async def test_analyze_portfolio_no_price_data(
        self,
        service,
        mock_market_data_repo,
        valid_csv_content
    ):
        """Test analysis when no price data is available"""
        # Setup
        file = UploadFile(
            filename="test.csv",
            file=BytesIO(valid_csv_content)
        )
        async def mock_to_thread(func, *args, **kwargs):
            if func == service.market_data.get_price_history:
                return []
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=[])

            # Execute & Assert
            with pytest.raises(NoPriceDataException):
                await service.analyze_portfolio(file)

    @pytest.mark.asyncio
    async def test_analyze_portfolio_no_matching_tickers(
        self,
        service,
        mock_market_data_repo,
        valid_csv_content
    ):
        """Test analysis when no matching ticker data exists"""
        # Setup - price data for different tickers
        dates = [datetime(2024, 1, 1)]
        different_ticker_data = [
            SecurityPrice(date=dates[0], ticker="TSLA", price=200.0),
            SecurityPrice(date=dates[0], ticker="NVDA", price=400.0),
        ]
        call_count = [0]
        async def mock_to_thread(func, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return different_ticker_data
            elif call_count[0] == 2:
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=different_ticker_data)

            file = UploadFile(
                filename="test.csv",
                file=BytesIO(valid_csv_content)
            )

            # Execute & Assert
            with pytest.raises(NoMatchingTickerDataException):
                await service.analyze_portfolio(file)

    @pytest.mark.asyncio
    async def test_analyze_portfolio_partial_ticker_match(
        self,
        service,
        mock_market_data_repo,
        sample_price_data
    ):
        """Test analysis with partial ticker matches"""
        # Setup - CSV with 3 tickers, but only 2 have price data
        data = {
            'name': ['AAPL', 'MSFT', 'GOOGL'],
            'weight': [0.4, 0.4, 0.2]
        }
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False).encode('utf-8')
        file = UploadFile(
            filename="test.csv",
            file=BytesIO(csv_content)
        )
        # Only return data for AAPL and MSFT
        call_count = [0]
        async def mock_to_thread(func, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return sample_price_data
            elif call_count[0] == 2:
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=sample_price_data)

            # Execute
            result = await service.analyze_portfolio(file)

            # Assertions - should work with available tickers
            assert result.etf_name == "test"
            assert len(result.latest_prices) == 2  # Only AAPL and MSFT
            assert all(ticker in ["AAPL", "MSFT"] for ticker in [p.ticker for p in result.latest_prices])

    @pytest.mark.asyncio
    async def test_analyze_portfolio_weights_normalization(
        self,
        service,
        mock_market_data_repo,
        sample_price_data
    ):
        """Test that weights are properly handled (case-insensitive ticker matching)"""
        # Setup - CSV with lowercase tickers
        data = {
            'name': ['aapl', 'msft'],  # lowercase
            'weight': [0.6, 0.4]
        }
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False).encode('utf-8')
        file = UploadFile(
            filename="test.csv",
            file=BytesIO(csv_content)
        )
        call_count = [0]
        async def mock_to_thread(func, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return sample_price_data
            elif call_count[0] == 2:
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=sample_price_data)

            # Execute
            result = await service.analyze_portfolio(file)

            # Assertions - should match uppercase tickers
            assert len(result.latest_prices) == 2
            assert all(ticker in ["AAPL", "MSFT"] for ticker in [p.ticker for p in result.latest_prices])

    @pytest.mark.asyncio
    async def test_analyze_portfolio_calculates_nav_correctly(
        self,
        service,
        mock_market_data_repo,
        sample_price_data
    ):
        """Test that NAV is calculated correctly"""
        # Setup
        data = {
            'name': ['AAPL', 'MSFT'],
            'weight': [0.5, 0.5]  # Equal weights
        }
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False).encode('utf-8')
        file = UploadFile(
            filename="test.csv",
            file=BytesIO(csv_content)
        )
        call_count = [0]
        async def mock_to_thread(func, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return sample_price_data
            elif call_count[0] == 2:
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=sample_price_data)

            # Execute
            result = await service.analyze_portfolio(file)

            # Assertions
            # Latest prices: AAPL=152.0, MSFT=302.0
            # Weighted: 0.5 * 152.0 + 0.5 * 302.0 = 76.0 + 151.0 = 227.0
            assert result.latest_close == 227.0
            assert len(result.etf_time_series) == 3
            # First day: 0.5 * 150.0 + 0.5 * 300.0 = 225.0
            assert result.etf_time_series[0].nav == 225.0

    @pytest.mark.asyncio
    async def test_analyze_portfolio_with_filename_extraction(
        self,
        service,
        mock_market_data_repo,
        valid_csv_content,
        sample_price_data
    ):
        """Test that ETF name is extracted from filename"""
        # Setup
        file = UploadFile(
            filename="my_custom_portfolio.csv",
            file=BytesIO(valid_csv_content)
        )
        call_count = [0]
        async def mock_to_thread(func, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return sample_price_data
            elif call_count[0] == 2:
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=sample_price_data)

            # Execute
            result = await service.analyze_portfolio(file)

            # Assertions
            assert result.etf_name == "my_custom_portfolio"

    @pytest.mark.asyncio
    async def test_analyze_portfolio_no_filename(
        self,
        service,
        mock_market_data_repo,
        valid_csv_content,
        sample_price_data
    ):
        """Test analysis with no filename"""
        # Setup
        file = UploadFile(
            filename=None,
            file=BytesIO(valid_csv_content)
        )
        call_count = [0]
        async def mock_to_thread(func, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return sample_price_data
            elif call_count[0] == 2:
                return func(*args, **kwargs)
            return func(*args, **kwargs)
        
        with patch('asyncio.to_thread', side_effect=mock_to_thread):
            mock_market_data_repo.get_price_history = Mock(return_value=sample_price_data)

            # Execute
            result = await service.analyze_portfolio(file)

            # Assertions
            assert result.etf_name == "ETF"  # Default name
