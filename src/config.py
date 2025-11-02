"""
Configuration module for MCP Trading Server
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for API keys and settings"""

    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

    # Google Cloud / Vertex AI (optional)
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")

    # API Endpoints
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    NEWSDATA_BASE_URL = "https://newsdata.io/api/1/news"

    # Rate Limiting
    ALPHA_VANTAGE_RATE_LIMIT = 5  # requests per minute
    NEWSDATA_DAILY_LIMIT = 200

    # Cache settings
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 minutes in seconds

    # FinBERT model
    FINBERT_MODEL = "ProsusAI/finbert"

    @classmethod
    def validate(cls):
        """Validate that required API keys are set"""
        errors = []

        if not cls.ALPHA_VANTAGE_API_KEY:
            errors.append("ALPHA_VANTAGE_API_KEY not set in .env file")

        if not cls.NEWSDATA_API_KEY:
            errors.append("NEWSDATA_API_KEY not set in .env file")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Warning: {e}")
    print("Please create a .env file with your API keys. See .env.example for reference.")
