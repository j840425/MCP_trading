"""
Sentiment analysis using FinBERT
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Any, List, Optional
from .news_client import NewsClient
from ..config import Config


class SentimentAnalyzer:
    """Sentiment analyzer using FinBERT model"""

    def __init__(self):
        self.news_client = NewsClient()
        self.model_name = Config.FINBERT_MODEL
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load FinBERT model and tokenizer"""
        try:
            print(f"Loading FinBERT model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.eval()
            print("FinBERT model loaded successfully")
        except Exception as e:
            print(f"Warning: Failed to load FinBERT model: {e}")
            print("Sentiment analysis will not be available")

    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.model or not self.tokenizer:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'error': 'Model not loaded'
            }

        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )

            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # FinBERT outputs: [positive, negative, neutral]
            scores = predictions[0].tolist()
            labels = ['positive', 'negative', 'neutral']

            # Get dominant sentiment
            max_score_idx = scores.index(max(scores))
            sentiment = labels[max_score_idx]
            confidence = scores[max_score_idx]

            # Calculate overall score (-1 to 1)
            overall_score = scores[0] - scores[1]  # positive - negative

            return {
                'sentiment': sentiment,
                'score': overall_score,
                'confidence': confidence,
                'scores': {
                    'positive': scores[0],
                    'negative': scores[1],
                    'neutral': scores[2]
                }
            }

        except Exception as e:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'error': str(e)
            }

    def analyze_news_sentiment(
        self,
        symbol: str,
        news_limit: int = 10,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of news for a symbol

        Args:
            symbol: Stock ticker
            news_limit: Number of news articles to analyze
            language: Language code

        Returns:
            Dictionary with aggregated sentiment analysis
        """
        # Get news
        try:
            news_articles = self.news_client.get_financial_news(
                symbol=symbol,
                limit=news_limit,
                language=language
            )
        except Exception as e:
            return {
                'symbol': symbol,
                'error': f"Failed to fetch news: {str(e)}",
                'sentiment': 'neutral',
                'score': 0.0
            }

        if not news_articles:
            return {
                'symbol': symbol,
                'error': 'No news articles found',
                'sentiment': 'neutral',
                'score': 0.0
            }

        # Analyze each article
        analyzed_articles = []
        for article in news_articles:
            # Combine title and description for analysis
            text = f"{article['title']} {article.get('description', '')}"

            sentiment_result = self._analyze_text(text)

            analyzed_articles.append({
                'title': article['title'],
                'url': article['url'],
                'published_at': article['published_at'],
                'source': article['source'],
                'sentiment': sentiment_result['sentiment'],
                'score': sentiment_result['score'],
                'confidence': sentiment_result['confidence']
            })

        # Calculate aggregated sentiment
        total_score = sum(a['score'] for a in analyzed_articles)
        avg_score = total_score / len(analyzed_articles)

        # Count sentiments
        sentiment_counts = {
            'positive': sum(1 for a in analyzed_articles if a['sentiment'] == 'positive'),
            'negative': sum(1 for a in analyzed_articles if a['sentiment'] == 'negative'),
            'neutral': sum(1 for a in analyzed_articles if a['sentiment'] == 'neutral')
        }

        # Determine overall sentiment
        if avg_score > 0.2:
            overall_sentiment = 'positive'
        elif avg_score < -0.2:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        # Calculate confidence
        avg_confidence = sum(a['confidence'] for a in analyzed_articles) / len(analyzed_articles)

        return {
            'symbol': symbol,
            'overall_sentiment': overall_sentiment,
            'sentiment_score': avg_score,
            'confidence': avg_confidence,
            'articles_analyzed': len(analyzed_articles),
            'sentiment_distribution': sentiment_counts,
            'articles': analyzed_articles,
            'interpretation': self._interpret_sentiment(avg_score, sentiment_counts)
        }

    def _interpret_sentiment(self, score: float, counts: Dict[str, int]) -> str:
        """Generate human-readable interpretation of sentiment"""
        total = sum(counts.values())

        if score > 0.3:
            return f"Strongly positive sentiment. {counts['positive']}/{total} articles are positive."
        elif score > 0.1:
            return f"Moderately positive sentiment. {counts['positive']}/{total} articles are positive."
        elif score < -0.3:
            return f"Strongly negative sentiment. {counts['negative']}/{total} articles are negative."
        elif score < -0.1:
            return f"Moderately negative sentiment. {counts['negative']}/{total} articles are negative."
        else:
            return f"Neutral sentiment. Market sentiment is mixed or unclear."

    def analyze_custom_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of custom text

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis result
        """
        return self._analyze_text(text)
