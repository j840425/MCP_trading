#!/usr/bin/env python3
"""
MCP Trading Quantitative Analysis Server

Servidor MCP que proporciona 12 herramientas para análisis cuantitativo de trading:
- 3 herramientas de datos de mercado (precios, históricos, quotes)
- 4 herramientas de indicadores técnicos (tendencia, momentum, volatilidad, volumen)
- 2 herramientas de análisis de noticias (búsqueda y sentiment con FinBERT)
- 3 herramientas de señales de trading (técnicas, fundamentales, híbridas)

Este servidor implementa el protocolo MCP (Model Context Protocol) de Anthropic,
permitiendo a Claude AI acceder a datos financieros en tiempo real y realizar
análisis cuantitativos complejos.

Author: j840425
Version: 1.0.0
"""

import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from src.market_data import AlphaVantageClient
from src.indicators import IndicatorCalculator
from src.news_analysis import NewsClient, SentimentAnalyzer
from src.signals import SignalGenerator

# Inicializar el servidor MCP con identificador único
server = Server("mcp-trading-server")

# Inicializar clientes y analizadores
# Estos objetos se instancian una sola vez y se reutilizan para todas las llamadas
market_client = AlphaVantageClient()  # Cliente Alpha Vantage para datos de mercado
indicator_calculator = IndicatorCalculator()  # Calculadora de indicadores técnicos
news_client = NewsClient()  # Cliente NewsData.io para noticias
sentiment_analyzer = SentimentAnalyzer()  # Analizador FinBERT para sentiment
signal_generator = SignalGenerator()  # Generador de señales de trading


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Lista todas las herramientas MCP disponibles.

    Esta función es llamada por Claude cuando inicia la conexión con el servidor
    para descubrir qué herramientas están disponibles y cómo usarlas.

    Returns:
        list[Tool]: Lista de 12 objetos Tool con sus definiciones, schemas y descripciones.
                    Cada Tool incluye:
                    - name: Identificador único de la herramienta
                    - description: Descripción de qué hace y cuándo usarla
                    - inputSchema: JSON Schema que define los parámetros requeridos

    Note:
        Las descripciones DEBEN estar en inglés para que Claude las interprete correctamente.
    """
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
    """
    Maneja las llamadas a las herramientas MCP.

    Esta función es invocada por Claude cuando decide usar una herramienta.
    Recibe el nombre de la herramienta y sus argumentos, ejecuta la lógica
    correspondiente y devuelve el resultado en formato JSON.

    Args:
        name (str): Nombre de la herramienta a ejecutar (ej: "get_current_price")
        arguments (dict): Diccionario con los parámetros de la herramienta
                         (ej: {"symbol": "AAPL"})

    Returns:
        list[TextContent]: Lista con un objeto TextContent que contiene:
                          - El resultado en formato JSON si la ejecución fue exitosa
                          - Un objeto de error en JSON si ocurrió una excepción

    Raises:
        No lanza excepciones directamente, todas se capturan y se devuelven como JSON.

    Example:
        >>> # Claude llama: get_current_price con {"symbol": "AAPL"}
        >>> # Servidor devuelve: {"symbol": "AAPL", "price": 178.45, ...}
    """

    try:
        # ============================================================
        # MARKET DATA TOOLS (3)
        # Herramientas para obtener datos de mercado de Alpha Vantage
        # ============================================================

        if name == "get_current_price":
            result = market_client.get_current_price(arguments["symbol"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_historical_data":
            # Obtener datos históricos OHLCV del mercado
            df = market_client.get_historical_data(
                symbol=arguments["symbol"],
                start_date=arguments["start_date"],
                end_date=arguments["end_date"],
                interval=arguments.get("interval", "daily")
            )
            # Formatear respuesta limitando a 100 filas para evitar payloads muy grandes
            result = {
                "symbol": arguments["symbol"],
                "rows": len(df),
                "columns": list(df.columns),
                "date_range": f"{df.index[0]} to {df.index[-1]}",
                "data": df.to_dict(orient="records")[:100]  # Limitar a primeras 100 filas
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_quote_info":
            # Obtener información completa del activo (precio + fundamentales)
            result = market_client.get_quote_info(arguments["symbol"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # ============================================================
        # TECHNICAL INDICATOR TOOLS (4)
        # Herramientas para calcular indicadores técnicos con pandas-ta
        # ============================================================

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

        # ============================================================
        # NEWS ANALYSIS TOOLS (2)
        # Herramientas para análisis de noticias y sentiment con FinBERT
        # ============================================================

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

        # ============================================================
        # TRADING SIGNAL TOOLS (3)
        # Herramientas para generar señales de trading (BUY/SELL/HOLD)
        # ============================================================

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
            # Herramienta desconocida
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        # Capturar cualquier error y devolverlo en formato JSON
        # Esto permite que Claude vea el error y pueda informar al usuario
        error_result = {
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main():
    """
    Función principal que inicia el servidor MCP.

    Crea un servidor stdio (comunicación por entrada/salida estándar) y
    ejecuta el loop principal del servidor MCP. El servidor permanece
    activo esperando comandos de Claude hasta que se cierra la conexión.

    Este es el punto de entrada cuando Claude ejecuta el comando configurado
    en .mcp.json o claude_desktop_config.json.
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    # Punto de entrada cuando se ejecuta directamente: python server.py
    import asyncio
    asyncio.run(main())
