"""
Alpha Vantage API client for market data
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import time
from ..config import Config


class AlphaVantageClient:
    """Client for Alpha Vantage API"""

    def __init__(self):
        self.api_key = Config.ALPHA_VANTAGE_API_KEY
        self.base_url = Config.ALPHA_VANTAGE_BASE_URL
        self.last_request_time = 0
        self.rate_limit_delay = 60 / Config.ALPHA_VANTAGE_RATE_LIMIT  # seconds between requests

    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)

        self.last_request_time = time.time()

    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make API request with rate limiting"""
        self._rate_limit()

        params['apikey'] = self.api_key

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")

            if "Note" in data:
                raise ValueError(f"Alpha Vantage Rate Limit: {data['Note']}")

            return data

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Alpha Vantage: {str(e)}")

    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current price for a symbol

        Args:
            symbol: Stock ticker (e.g., "AAPL") or forex pair (e.g., "EUR/USD")

        Returns:
            Dictionary with current price information
        """
        # Check if it's a forex pair
        if '/' in symbol:
            from_currency, to_currency = symbol.split('/')
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': from_currency,
                'to_currency': to_currency
            }
            data = self._make_request(params)

            if "Realtime Currency Exchange Rate" not in data:
                raise ValueError(f"No data found for {symbol}")

            rate_data = data["Realtime Currency Exchange Rate"]

            return {
                'symbol': symbol,
                'price': float(rate_data['5. Exchange Rate']),
                'timestamp': rate_data['6. Last Refreshed'],
                'from_currency': rate_data['1. From_Currency Code'],
                'to_currency': rate_data['3. To_Currency Code'],
                'bid_price': float(rate_data.get('8. Bid Price', 0)),
                'ask_price': float(rate_data.get('9. Ask Price', 0))
            }
        else:
            # Stock symbol
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol
            }
            data = self._make_request(params)

            if "Global Quote" not in data or not data["Global Quote"]:
                raise ValueError(f"No data found for {symbol}")

            quote = data["Global Quote"]

            return {
                'symbol': quote['01. symbol'],
                'price': float(quote['05. price']),
                'timestamp': quote['07. latest trading day'],
                'change': float(quote['09. change']),
                'change_percent': quote['10. change percent'],
                'volume': int(quote['06. volume']),
                'open': float(quote['02. open']),
                'high': float(quote['03. high']),
                'low': float(quote['04. low']),
                'previous_close': float(quote['08. previous close'])
            }

    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = 'daily'
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data

        Args:
            symbol: Stock ticker
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Time interval (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)

        Returns:
            DataFrame with OHLCV data
        """
        interval_map = {
            '1min': 'TIME_SERIES_INTRADAY',
            '5min': 'TIME_SERIES_INTRADAY',
            '15min': 'TIME_SERIES_INTRADAY',
            '30min': 'TIME_SERIES_INTRADAY',
            '60min': 'TIME_SERIES_INTRADAY',
            'daily': 'TIME_SERIES_DAILY',
            'weekly': 'TIME_SERIES_WEEKLY',
            'monthly': 'TIME_SERIES_MONTHLY'
        }

        if interval not in interval_map:
            raise ValueError(f"Invalid interval: {interval}")

        function = interval_map[interval]
        params = {
            'function': function,
            'symbol': symbol,
            'outputsize': 'full'
        }

        # Add interval parameter for intraday data
        if 'INTRADAY' in function:
            params['interval'] = interval

        data = self._make_request(params)

        # Find the time series key
        time_series_key = None
        for key in data.keys():
            if 'Time Series' in key:
                time_series_key = key
                break

        if not time_series_key:
            raise ValueError(f"No time series data found for {symbol}")

        time_series = data[time_series_key]

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Rename columns
        column_map = {
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        }
        df = df.rename(columns=column_map)

        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])

        # Filter by date range
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df.index >= start) & (df.index <= end)]

        return df

    def get_quote_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive quote information

        Args:
            symbol: Stock ticker

        Returns:
            Dictionary with comprehensive quote information
        """
        # Get current quote
        current_quote = self.get_current_price(symbol)

        # Get company overview
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }

        try:
            overview = self._make_request(params)

            # Combine data
            result = {
                **current_quote,
                'company_name': overview.get('Name', 'N/A'),
                'description': overview.get('Description', 'N/A'),
                'sector': overview.get('Sector', 'N/A'),
                'industry': overview.get('Industry', 'N/A'),
                'market_cap': overview.get('MarketCapitalization', 'N/A'),
                'pe_ratio': overview.get('PERatio', 'N/A'),
                'eps': overview.get('EPS', 'N/A'),
                'dividend_yield': overview.get('DividendYield', 'N/A'),
                '52_week_high': overview.get('52WeekHigh', 'N/A'),
                '52_week_low': overview.get('52WeekLow', 'N/A'),
                'beta': overview.get('Beta', 'N/A')
            }

            return result

        except Exception as e:
            # If overview fails, just return current quote
            return current_quote
