"""
Módulo de configuración para el Servidor MCP de Trading.

Este módulo centraliza todas las configuraciones del servidor, incluyendo:
- API keys de servicios externos (Alpha Vantage, NewsData.io)
- URLs base de las APIs
- Límites de rate limiting
- Configuraciones de caché
- Modelo de FinBERT para análisis de sentiment

Las configuraciones se cargan desde variables de entorno definidas en el archivo .env
siguiendo las mejores prácticas de seguridad (nunca hardcodear credenciales).

Author: j840425
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
# load_dotenv() busca automáticamente el archivo .env y carga sus variables
load_dotenv()

class Config:
    """
    Clase de configuración centralizada para el servidor MCP.

    Todos los módulos importan esta clase para acceder a configuraciones.
    Las variables se cargan desde el archivo .env para mantener las
    credenciales seguras y fuera del control de versiones.

    Attributes:
        ALPHA_VANTAGE_API_KEY (str): API key de Alpha Vantage para datos de mercado
        NEWSDATA_API_KEY (str): API key de NewsData.io para noticias financieras
        ALPHA_VANTAGE_BASE_URL (str): URL base de la API de Alpha Vantage
        NEWSDATA_BASE_URL (str): URL base de la API de NewsData.io
        ALPHA_VANTAGE_RATE_LIMIT (int): Límite de requests por minuto (plan gratuito: 5)
        NEWSDATA_DAILY_LIMIT (int): Límite de noticias por día (plan gratuito: 200)
        CACHE_ENABLED (bool): Habilitar caché para optimizar requests
        CACHE_TTL (int): Tiempo de vida del caché en segundos (5 minutos)
        FINBERT_MODEL (str): Nombre del modelo FinBERT de Hugging Face

    Example:
        >>> from src.config import Config
        >>> api_key = Config.ALPHA_VANTAGE_API_KEY
        >>> Config.validate()  # Verifica que las API keys estén configuradas
    """

    # ============================================================
    # API KEYS (cargar desde archivo .env)
    # ============================================================
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

    # ============================================================
    # GOOGLE CLOUD / VERTEX AI (opcional, para futuras extensiones)
    # ============================================================
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")

    # ============================================================
    # API ENDPOINTS (URLs base de los servicios)
    # ============================================================
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    NEWSDATA_BASE_URL = "https://newsdata.io/api/1/news"

    # ============================================================
    # RATE LIMITING (límites de uso de APIs gratuitas)
    # ============================================================
    ALPHA_VANTAGE_RATE_LIMIT = 5  # requests por minuto en plan gratuito
    NEWSDATA_DAILY_LIMIT = 200  # noticias por día en plan gratuito

    # ============================================================
    # CACHE SETTINGS (optimización de requests)
    # ============================================================
    CACHE_ENABLED = True  # Habilitar caché de respuestas
    CACHE_TTL = 300  # Tiempo de vida del caché: 5 minutos (300 segundos)

    # ============================================================
    # FINBERT MODEL (modelo NLP para análisis de sentiment)
    # ============================================================
    FINBERT_MODEL = "ProsusAI/finbert"  # Modelo pre-entrenado de Hugging Face

    @classmethod
    def validate(cls):
        """
        Valida que las API keys requeridas estén configuradas.

        Este método se ejecuta automáticamente al importar el módulo
        para detectar problemas de configuración tempranamente.

        Returns:
            bool: True si todas las validaciones pasan

        Raises:
            ValueError: Si falta alguna API key requerida

        Example:
            >>> try:
            ...     Config.validate()
            ...     print("Configuración válida")
            ... except ValueError as e:
            ...     print(f"Error de configuración: {e}")
        """
        errors = []

        # Verificar API key de Alpha Vantage (requerida)
        if not cls.ALPHA_VANTAGE_API_KEY:
            errors.append("ALPHA_VANTAGE_API_KEY not set in .env file")

        # Verificar API key de NewsData.io (requerida)
        if not cls.NEWSDATA_API_KEY:
            errors.append("NEWSDATA_API_KEY not set in .env file")

        # Si hay errores, lanzar excepción con todos los problemas encontrados
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True

# ============================================================
# VALIDACIÓN AUTOMÁTICA AL IMPORTAR
# Valida la configuración cuando se importa el módulo
# Si falta alguna API key, muestra un warning pero no detiene la ejecución
# ============================================================
try:
    Config.validate()
except ValueError as e:
    print(f"Warning: {e}")
    print("Please create a .env file with your API keys. See .env.example for reference.")
