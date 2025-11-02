"""
NewsData.io API client for financial news
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..config import Config


class NewsClient:
    """Client for NewsData.io API"""

    def __init__(self):
        self.api_key = Config.NEWSDATA_API_KEY
        self.base_url = Config.NEWSDATA_BASE_URL

    def get_financial_news(
        self,
        symbol: str,
        limit: int = 10,
        language: str = "en",
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get financial news for a symbol

        Args:
            symbol: Stock ticker or search keyword
            limit: Number of news articles to retrieve
            language: Language code (default: "en")
            days_back: Number of days to look back (default: 7)

        Returns:
            List of news articles
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Build query
        query = f"{symbol} OR stock OR trading"

        params = {
            'apikey': self.api_key,
            'q': query,
            'language': language,
            'category': 'business',
            'size': min(limit, 50)  # API max per request is 50
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'success':
                raise ValueError(f"NewsData.io API Error: {data.get('message', 'Unknown error')}")

            articles = []
            for result in data.get('results', [])[:limit]:
                article = {
                    'title': result.get('title', ''),
                    'description': result.get('description', ''),
                    'content': result.get('content', ''),
                    'url': result.get('link', ''),
                    'published_at': result.get('pubDate', ''),
                    'source': result.get('source_id', ''),
                    'keywords': result.get('keywords', [])
                }
                articles.append(article)

            return articles

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to NewsData.io: {str(e)}")

    def search_news(
        self,
        keywords: List[str],
        limit: int = 10,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Search news by keywords

        Args:
            keywords: List of keywords to search
            limit: Number of articles
            language: Language code

        Returns:
            List of news articles
        """
        query = " OR ".join(keywords)

        params = {
            'apikey': self.api_key,
            'q': query,
            'language': language,
            'category': 'business',
            'size': min(limit, 50)
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'success':
                raise ValueError(f"NewsData.io API Error: {data.get('message', 'Unknown error')}")

            articles = []
            for result in data.get('results', [])[:limit]:
                article = {
                    'title': result.get('title', ''),
                    'description': result.get('description', ''),
                    'content': result.get('content', ''),
                    'url': result.get('link', ''),
                    'published_at': result.get('pubDate', ''),
                    'source': result.get('source_id', ''),
                    'keywords': result.get('keywords', [])
                }
                articles.append(article)

            return articles

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to NewsData.io: {str(e)}")
