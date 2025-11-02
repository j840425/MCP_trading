#!/usr/bin/env python3
"""
MCP Trading Quantitative Analysis Server

This server provides 12 tools for quantitative trading analysis:
- 3 market data tools
- 4 technical indicator tools
- 2 news analysis tools
- 3 trading signal tools
"""

import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from src.market_data import AlphaVantageClient
from src.indicators import IndicatorCalculator
from src.news_analysis import NewsClient, SentimentAnalyzer
from src.signals import SignalGenerator

# Initialize server
server = Server("mcp-trading-server")

# Initialize clients and analyzers
market_client = AlphaVantageClient()
indicator_calculator = IndicatorCalculator()
news_client = NewsClient()
sentiment_analyzer = SentimentAnalyzer()
signal_generator = SignalGenerator()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available trading analysis tools"""
    return [
        # Market Data Tools (3)
        Tool(
            name="get_current_price",
            description="Get current price for a stock or forex pair. Supports stocks (e.g., 'AAPL') and forex pairs (e.g., 'EUR/USD').",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker (e.g., 'AAPL') or forex pair (e.g., 'EUR/USD')"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_historical_data",
            description="Get historical OHLCV (Open, High, Low, Close, Volume) data for a stock.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "interval": {
                        "type": "string",
                        "description": "Time interval: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly",
                        "default": "daily"
                    }
                },
                "required": ["symbol", "start_date", "end_date"]
            }
        ),
        Tool(
            name="get_quote_info",
            description="Get comprehensive quote information including company details, fundamentals, and current price.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["symbol"]
            }
        ),

        # Technical Indicator Tools (4)
        Tool(
            name="calculate_trend_indicators",
            description="Calculate trend indicators: SMA, EMA, MACD, ADX, AROON, PSAR, SUPERTREND, DEMA",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "indicators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of indicators: SMA, EMA, MACD, ADX, AROON, PSAR, SUPERTREND, DEMA"
                    },
                    "periods": {
                        "type": "object",
                        "description": "Optional periods for each indicator (e.g., {'SMA': 20, 'EMA': 50})",
                        "additionalProperties": {"type": "integer"}
                    }
                },
                "required": ["symbol", "indicators"]
            }
        ),
        Tool(
            name="calculate_momentum_indicators",
            description="Calculate momentum indicators: RSI, STOCHASTIC, CCI, WILLR, ROC, MFI, TSI, MOMENTUM",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "indicators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of indicators: RSI, STOCHASTIC, CCI, WILLR, ROC, MFI, TSI, MOMENTUM"
                    },
                    "periods": {
                        "type": "object",
                        "description": "Optional periods for each indicator (e.g., {'RSI': 14})",
                        "additionalProperties": {"type": "integer"}
                    }
                },
                "required": ["symbol", "indicators"]
            }
        ),
        Tool(
            name="calculate_volatility_indicators",
            description="Calculate volatility indicators: BBANDS, ATR, KELTNER, STDDEV, DONCHIAN, ULCER",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "indicators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of indicators: BBANDS, ATR, KELTNER, STDDEV, DONCHIAN, ULCER"
                    },
                    "periods": {
                        "type": "object",
                        "description": "Optional periods for each indicator (e.g., {'BBANDS': 20})",
                        "additionalProperties": {"type": "integer"}
                    }
                },
                "required": ["symbol", "indicators"]
            }
        ),
        Tool(
            name="calculate_volume_indicators",
            description="Calculate volume indicators: OBV, VWAP, AD, CMF, VO, PVT",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "indicators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of indicators: OBV, VWAP, AD, CMF, VO, PVT"
                    },
                    "periods": {
                        "type": "object",
                        "description": "Optional periods for each indicator (e.g., {'CMF': 20})",
                        "additionalProperties": {"type": "integer"}
                    }
                },
                "required": ["symbol", "indicators"]
            }
        ),

        # News Analysis Tools (2)
        Tool(
            name="get_financial_news",
            description="Get recent financial news articles for a stock or keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker or search keyword"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of news articles to retrieve (default: 10)",
                        "default": 10
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (default: 'en')",
                        "default": "en"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="analyze_news_sentiment",
            description="Analyze sentiment of financial news using FinBERT. Returns overall sentiment (positive/negative/neutral), sentiment score, and article-level analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "news_limit": {
                        "type": "integer",
                        "description": "Number of news articles to analyze (default: 10)",
                        "default": 10
                    }
                },
                "required": ["symbol"]
            }
        ),

        # Trading Signal Tools (3)
        Tool(
            name="generate_technical_signal",
            description="Generate trading signal based on technical indicators. Supports simple strategies (RSI, MACD, SMA_CROSS, BBANDS) and compound strategies combining multiple indicators.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "strategy_type": {
                        "type": "string",
                        "description": "'simple' for single indicator, 'compound' for multiple indicators",
                        "default": "simple"
                    },
                    "indicators_config": {
                        "type": "object",
                        "description": "Strategy configuration. For simple: {'strategy': 'RSI', 'rsi_period': 14}. For compound: see documentation.",
                        "additionalProperties": True
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="generate_fundamental_signal",
            description="Generate trading signal based on news sentiment analysis. Uses FinBERT to analyze recent news and generate BUY/SELL/HOLD recommendation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "news_count": {
                        "type": "integer",
                        "description": "Number of news articles to analyze (default: 10)",
                        "default": 10
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Sentiment threshold for signal generation (default: 0.15)",
                        "default": 0.15
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="generate_hybrid_signal",
            description="Generate hybrid trading signal combining technical and fundamental analysis. Provides weighted combination of technical indicators and news sentiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "technical_weight": {
                        "type": "number",
                        "description": "Weight for technical analysis (0-1, default: 0.6)",
                        "default": 0.6
                    },
                    "fundamental_weight": {
                        "type": "number",
                        "description": "Weight for fundamental analysis (0-1, default: 0.4)",
                        "default": 0.4
                    },
                    "technical_config": {
                        "type": "object",
                        "description": "Configuration for technical analysis",
                        "additionalProperties": True
                    },
                    "news_config": {
                        "type": "object",
                        "description": "Configuration for news analysis",
                        "additionalProperties": True
                    }
                },
                "required": ["symbol"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    try:
        # Market Data Tools
        if name == "get_current_price":
            result = market_client.get_current_price(arguments["symbol"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_historical_data":
            df = market_client.get_historical_data(
                symbol=arguments["symbol"],
                start_date=arguments["start_date"],
                end_date=arguments["end_date"],
                interval=arguments.get("interval", "daily")
            )
            result = {
                "symbol": arguments["symbol"],
                "rows": len(df),
                "columns": list(df.columns),
                "date_range": f"{df.index[0]} to {df.index[-1]}",
                "data": df.to_dict(orient="records")[:100]  # Limit to first 100 rows
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_quote_info":
            result = market_client.get_quote_info(arguments["symbol"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # Technical Indicator Tools
        elif name == "calculate_trend_indicators":
            result = indicator_calculator.calculate_trend_indicators(
                symbol=arguments["symbol"],
                indicators=arguments["indicators"],
                periods=arguments.get("periods")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "calculate_momentum_indicators":
            result = indicator_calculator.calculate_momentum_indicators(
                symbol=arguments["symbol"],
                indicators=arguments["indicators"],
                periods=arguments.get("periods")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "calculate_volatility_indicators":
            result = indicator_calculator.calculate_volatility_indicators(
                symbol=arguments["symbol"],
                indicators=arguments["indicators"],
                periods=arguments.get("periods")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "calculate_volume_indicators":
            result = indicator_calculator.calculate_volume_indicators(
                symbol=arguments["symbol"],
                indicators=arguments["indicators"],
                periods=arguments.get("periods")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # News Analysis Tools
        elif name == "get_financial_news":
            result = news_client.get_financial_news(
                symbol=arguments["symbol"],
                limit=arguments.get("limit", 10),
                language=arguments.get("language", "en")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "analyze_news_sentiment":
            result = sentiment_analyzer.analyze_news_sentiment(
                symbol=arguments["symbol"],
                news_limit=arguments.get("news_limit", 10)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # Trading Signal Tools
        elif name == "generate_technical_signal":
            result = signal_generator.generate_technical_signal(
                symbol=arguments["symbol"],
                strategy_type=arguments.get("strategy_type", "simple"),
                indicators_config=arguments.get("indicators_config")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "generate_fundamental_signal":
            result = signal_generator.generate_fundamental_signal(
                symbol=arguments["symbol"],
                news_count=arguments.get("news_count", 10),
                threshold=arguments.get("threshold", 0.15)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "generate_hybrid_signal":
            result = signal_generator.generate_hybrid_signal(
                symbol=arguments["symbol"],
                technical_weight=arguments.get("technical_weight", 0.6),
                fundamental_weight=arguments.get("fundamental_weight", 0.4),
                technical_config=arguments.get("technical_config"),
                news_config=arguments.get("news_config")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        error_result = {
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
