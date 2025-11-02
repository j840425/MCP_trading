# 📈 MCP Trading Quantitative Analysis Server

Sistema de análisis de trading cuantitativo implementado como servidor MCP (Model Context Protocol) que permite a Claude acceder y analizar datos financieros, calcular indicadores técnicos, evaluar sentiment de noticias y generar señales de trading para acciones y forex.

## ✨ Características Principales

- **12 herramientas MCP** organizadas en 4 categorías funcionales
- **Análisis técnico** con 28+ indicadores técnicos (RSI, MACD, Bollinger Bands, etc.)
- **Análisis de sentiment** usando FinBERT para noticias financieras
- **Señales de trading** técnicas, fundamentales e híbridas con scores de confianza
- **Datos en tiempo real** mediante Alpha Vantage API
- **Arquitectura modular** y extensible para fácil integración de nuevas fuentes

## 🏗️ Arquitectura

El sistema está organizado en capas modulares:

- **Servidor MCP**: Implementación del protocolo MCP con 12 herramientas
- **Datos de Mercado**: Cliente Alpha Vantage para precios y datos históricos
- **Indicadores Técnicos**: Cálculo automatizado con pandas-ta
- **Análisis NLP**: FinBERT para sentiment analysis de noticias financieras
- **Generador de Señales**: Combina análisis técnico y fundamental
- **Configuración**: Variables de entorno con python-dotenv

## 🚀 Instalación

### Requisitos

- Python 3.12+
- API Key de Alpha Vantage (gratis: https://www.alphavantage.co/support/#api-key)
- API Key de NewsData.io (gratis: https://newsdata.io/)

### Pasos

1. **Clonar el repositorio**
```bash
cd /ruta/a/pry_mcp_trading
```

2. **Crear entorno virtual**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar API keys**
```bash
cp .env.example .env
nano .env
```

Agregar tus claves:
```env
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
NEWSDATA_API_KEY=tu_api_key_aqui
```

5. **Probar conexión**
```bash
python test_connection.py
```

### Configurar Claude

#### Para Claude Desktop

Editar archivo de configuración según tu sistema operativo:

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Agregar configuración (reemplazar con tu ruta real):
```json
{
  "mcpServers": {
    "trading-quantitative": {
      "command": "/ruta/completa/a/pry_mcp_trading/.venv/bin/python",
      "args": [
        "/ruta/completa/a/pry_mcp_trading/server.py"
      ],
      "env": {
        "PYTHONPATH": "/ruta/completa/a/pry_mcp_trading"
      }
    }
  }
}
```

#### Para Claude Code (VSCode)

El archivo `.mcp.json` ya está configurado en la raíz del proyecto.

Asegúrate de tener en `.claude/settings.local.json`:
```json
{
  "enableAllProjectMcpServers": true
}
```

Recarga VSCode: `Ctrl+Shift+P` → "Developer: Reload Window"

### Verificación

Pregunta a Claude:
```
¿Qué herramientas MCP tienes disponibles?
```

Deberías ver las 12 herramientas de trading listadas.

## 🛠️ Tecnologías

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Protocol | MCP SDK | 1.0.0+ |
| Data API | Alpha Vantage | API v2 |
| News API | NewsData.io | API v1 |
| Análisis Técnico | pandas-ta | Latest |
| NLP Sentiment | FinBERT (transformers) | 4.57+ |
| ML Framework | PyTorch | 2.0+ |
| Data Processing | pandas, numpy | Latest |

## 📂 Estructura del Proyecto

```
pry_mcp_trading/
├── server.py                    # Servidor MCP principal
├── requirements.txt             # Dependencias Python
├── .env                         # API keys (no subir a git)
├── .env.example                 # Plantilla de configuración
├── .mcp.json                    # Config MCP para Claude Code
├── setup.sh                     # Script de instalación
├── test_connection.py           # Tests de conexión APIs
├── README.md                    # Esta documentación
├── .gitignore                   # Archivos ignorados
└── src/                         # Código fuente
    ├── config.py                # Configuración centralizada
    ├── market_data/             # Módulo de datos (3 tools)
    │   ├── __init__.py
    │   └── client.py            # Cliente Alpha Vantage
    ├── indicators/              # Módulo indicadores (4 tools)
    │   ├── __init__.py
    │   └── calculator.py        # Cálculo de indicadores
    ├── news_analysis/           # Módulo noticias (2 tools)
    │   ├── __init__.py
    │   ├── news_client.py       # Cliente NewsData.io
    │   └── sentiment_analyzer.py # FinBERT sentiment
    └── signals/                 # Módulo señales (3 tools)
        ├── __init__.py
        └── signal_generator.py  # Generador de señales
```

## 🔧 Herramientas MCP Disponibles

### 📊 Grupo 1: Datos de Mercado (3)

#### `get_current_price`
Obtiene precio actual de acciones o forex.
```
Ejemplo: "¿Cuál es el precio actual de AAPL?"
```

#### `get_historical_data`
Datos históricos OHLCV con múltiples intervalos (1min a monthly).
```
Ejemplo: "Muéstrame los datos históricos de TSLA de los últimos 3 meses"
```

#### `get_quote_info`
Información completa: precio, fundamentales, empresa.
```
Ejemplo: "Dame información completa sobre Microsoft (MSFT)"
```

### 📈 Grupo 2: Indicadores Técnicos (4)

#### `calculate_trend_indicators`
8 indicadores: SMA, EMA, MACD, ADX, AROON, PSAR, SUPERTREND, DEMA
```
Ejemplo: "Calcula el MACD y EMA(20) para AAPL"
```

#### `calculate_momentum_indicators`
8 indicadores: RSI, STOCHASTIC, CCI, WILLR, ROC, MFI, TSI, MOMENTUM
```
Ejemplo: "¿Cuál es el RSI actual de GOOGL?"
```

#### `calculate_volatility_indicators`
6 indicadores: BBANDS, ATR, KELTNER, STDDEV, DONCHIAN, ULCER
```
Ejemplo: "Calcula las Bandas de Bollinger para AMZN"
```

#### `calculate_volume_indicators`
6 indicadores: OBV, VWAP, AD, CMF, VO, PVT
```
Ejemplo: "Analiza el volumen de META con OBV y VWAP"
```

### 📰 Grupo 3: Análisis de Noticias (2)

#### `get_financial_news`
Obtiene últimas noticias financieras del activo.
```
Ejemplo: "Muéstrame las últimas noticias sobre Tesla"
```

#### `analyze_news_sentiment`
Analiza sentiment con FinBERT (positive/negative/neutral + score).
```
Ejemplo: "Analiza el sentiment de las noticias sobre Apple"
```

### 🎯 Grupo 4: Señales de Trading (3)

#### `generate_technical_signal`
Señales basadas en indicadores técnicos (simple o compuestas).
```
Ejemplo: "Dame una señal técnica para NVDA usando RSI"
```

#### `generate_fundamental_signal`
Señales basadas en sentiment de noticias con FinBERT.
```
Ejemplo: "¿Qué dicen las noticias sobre AMD? Dame una señal"
```

#### `generate_hybrid_signal`
Combina análisis técnico + fundamental con pesos configurables.
```
Ejemplo: "Genera una señal híbrida para Bitcoin"
```

## 📖 Ejemplos de Uso

### Análisis Básico
```
Usuario: "¿Cuál es el precio actual de Apple?"

Claude: [Llama get_current_price("AAPL")]
        El precio actual de Apple es $270.37
        - Cambio: -$1.03 (-0.38%)
        - Volumen: 86,167,123
        - Máximo: $277.32 | Mínimo: $269.16
```

### Análisis Técnico Completo
```
Usuario: "Analiza AAPL técnicamente"

Claude: [Ejecuta múltiples herramientas]
        📊 ANÁLISIS TÉCNICO DE APPLE (AAPL)

        Momentum:
        • RSI(14): 69.05 - NEUTRAL (cerca de sobrecompra)
        • Estocástico: 87.72 - SOBRECOMPRADO

        Tendencia:
        • Precio: $270.37
        • SMA(50): $248.25 - Precio 8.9% arriba ✓
        • EMA(20): $260.41 - Precio 3.8% arriba ✓

        🎯 SEÑAL: HOLD con sesgo alcista
```

### Análisis de Sentiment
```
Usuario: "Analiza el sentiment de noticias de Apple"

Claude: [Llama analyze_news_sentiment("AAPL")]
        📰 SENTIMENT ANALYSIS - APPLE

        Score: +0.25 (positivo moderado)
        Confianza: 89.7%

        Distribución:
        - 6 noticias positivas (60%)
        - 3 noticias negativas (30%)
        - 1 noticia neutral (10%)

        Interpretación: Sentiment mayormente positivo
```

### Señal de Trading Completa
```
Usuario: "Dame una recomendación de trading para AAPL"

Claude: [Genera señal híbrida]
        🎯 SEÑAL DE TRADING - APPLE (AAPL)

        RECOMENDACIÓN: HOLD (sesgo alcista)
        Confianza: 72%

        Análisis Técnico (60%):
        ✓ Tendencia alcista (SMA/EMA)
        ⚠️ Estocástico sobrecomprado

        Análisis Fundamental (40%):
        ✓ Sentiment positivo (+0.25)

        Plan sugerido:
        - Entrada: Esperar pullback a $260-265
        - Stop Loss: $255
        - Target: $280-285
```

## 🔑 Características Técnicas

### Procesamiento de Datos
- **Caché inteligente** para optimizar requests a APIs
- **Manejo de errores robusto** con reintentos automáticos
- **Validación de datos** con pandas para limpieza automática

### Análisis de Sentiment
- **FinBERT** especializado en textos financieros
- **Modelo pre-entrenado** de Hugging Face (ProsusAI/finbert)
- **Análisis por artículo** con agregación ponderada
- **Descarga automática** del modelo en primera ejecución

### Generación de Señales
- **Estrategias simples**: RSI, MACD, SMA Cross, Bollinger Bands
- **Estrategias compuestas**: Múltiples indicadores con pesos
- **Confluence scoring**: Combina señales para mayor confianza
- **Pesos configurables**: Ajusta balance técnico/fundamental

## ⚠️ Limitaciones

### Técnicas
- **Alpha Vantage gratis**: 25 requests/día, 5 requests/minuto
- **NewsData.io gratis**: 200 noticias/día
- **Delay de datos**: Hasta 15 minutos en plan gratuito
- **FinBERT**: Requiere 2GB RAM + 2GB disco para modelo

### Funcionales
- Solo **acciones globales y forex** (no opciones/futuros)
- Sentiment analysis en **inglés únicamente**
- **Solo análisis y señales** (no ejecuta trades)
- Indicadores calculados sobre **datos históricos disponibles**

## 🐛 Troubleshooting

### El servidor no se conecta
```bash
# Verificar rutas absolutas en configuración
pwd  # Copiar esta ruta

# Verificar dependencias
source .venv/bin/activate
pip list | grep -E "mcp|pandas|transformers"

# Test de conexión
python test_connection.py
```

### Error de API keys
```bash
# Verificar archivo .env existe
ls -la .env

# Verificar contenido
cat .env

# Test individual
python -c "from src.config import Config; print(Config.ALPHA_VANTAGE_API_KEY)"
```

### FinBERT no descarga
```bash
# Verificar espacio en disco
df -h

# Descargar manualmente
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
           AutoTokenizer.from_pretrained('ProsusAI/finbert'); \
           AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')"
```

### Rate limit exceeded
- **Solución temporal**: Esperar reset diario (medianoche UTC)
- **Solución permanente**: Upgrade a plan premium de Alpha Vantage
- **Workaround**: Implementar caché local con Redis/SQLite

### Claude no reconoce servidor (VSCode)
```bash
# Verificar .mcp.json
cat .mcp.json

# Verificar settings
cat .claude/settings.local.json

# Recargar VSCode
# Ctrl+Shift+P → "Developer: Reload Window"
```

## 🔐 Seguridad

**NUNCA subas a Git:**
- `.env` con API keys
- Archivos `*.pyc` o `__pycache__/`
- Directorio `.venv/`

**Ya configurado en `.gitignore`:**
```gitignore
.env
.venv/
__pycache__/
*.pyc
```

**Para producción:**
- Usa variables de entorno del sistema
- Rota API keys periódicamente
- Monitorea uso de APIs

## 📝 Desarrollo

### Agregar un Nuevo Indicador

1. Edita `src/indicators/calculator.py`
2. Agrega método para el nuevo indicador
3. Registra en `server.py` en la tool correspondiente
4. Actualiza documentación

Ejemplo:
```python
def calculate_custom_indicator(self, symbol: str, period: int = 14):
    """Calcula indicador personalizado"""
    df = self.market_client.get_historical_data(symbol, ...)
    result = df.ta.custom(length=period)
    return {
        "symbol": symbol,
        "value": result.iloc[-1],
        "interpretation": "..."
    }
```

### Testing Local
```bash
# Activar entorno
source .venv/bin/activate

# Test de conexión
python test_connection.py

# Test de herramienta específica
python -c "from src.market_data import AlphaVantageClient; \
           print(AlphaVantageClient().get_current_price('AAPL'))"

# Ejecutar servidor manualmente
python server.py
```

### Extensiones Futuras
- [ ] Soporte para criptomonedas (Binance, CoinGecko)
- [ ] Backtesting automatizado de estrategias
- [ ] Alertas en tiempo real vía webhooks
- [ ] Dashboard web con Streamlit/Dash
- [ ] Base de datos para histórico (PostgreSQL)
- [ ] Machine Learning para optimización de parámetros
- [ ] Paper trading con brokers (Alpaca, Interactive Brokers)
- [ ] Caché distribuido con Redis
- [ ] Análisis de correlaciones entre activos

## 🌐 Recursos

### Documentación APIs
- [Alpha Vantage Docs](https://www.alphavantage.co/documentation/)
- [NewsData.io Docs](https://newsdata.io/documentation)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)

### Librerías Python
- [pandas-ta](https://github.com/twopirllc/pandas-ta) - Indicadores técnicos
- [transformers](https://huggingface.co/docs/transformers/) - Hugging Face
- [FinBERT](https://huggingface.co/ProsusAI/finbert) - Sentiment financiero

### Trading Education
- [Investopedia](https://www.investopedia.com/technical-analysis-4689657)
- [TradingView](https://www.tradingview.com/)

## 📋 Comandos Útiles

```bash
# Activar/desactivar entorno
source .venv/bin/activate
deactivate

# Gestión de dependencias
pip list
pip install --upgrade -r requirements.txt

# Limpieza
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Tamaño del proyecto
du -sh .

# Test de APIs
python test_connection.py
```

## 👤 Autoría y Desarrollo

**Diseño y Arquitectura:** Jean Carlo Gómez Ponce
- Conceptualización del sistema
- Decisiones de arquitectura MCP
- Dirección del desarrollo
- Integración de herramientas

**Implementación:** Código generado con Claude AI (Anthropic) bajo supervisión y especificaciones del autor

**Nota sobre el uso de IA:** Este proyecto fue desarrollado mediante pair programming con IA. El diseño, la arquitectura y las decisiones técnicas son del autor humano. La implementación del código fue asistida por Claude AI siguiendo las especificaciones proporcionadas.

## 🙏 Agradecimientos

- [Anthropic](https://anthropic.com) por Claude AI
- [MCP Protocol](https://modelcontextprotocol.io/) por el estándar de comunicación
- [Alpha Vantage](https://www.alphavantage.co/) por datos de mercado
- [NewsData.io](https://newsdata.io/) por noticias financieras
- [Hugging Face](https://huggingface.co/) por FinBERT
- Comunidad open source de Python

## ⚖️ Licencia

Este proyecto es para **uso educativo únicamente**. No se ofrece ninguna garantía.

## ⚠️ Disclaimer

**IMPORTANTE:** Este software es solo para propósitos educativos e informativos. **NO constituye asesoría financiera, de inversión, ni recomendación de trading.**

El trading y la inversión en mercados financieros conllevan **riesgos significativos** y pueden resultar en **pérdida parcial o total del capital**. Los resultados pasados no garantizan rendimientos futuros.

**Siempre consulta con un asesor financiero profesional** antes de tomar decisiones de inversión. El autor no se hace responsable de las pérdidas o daños que puedan resultar del uso de este software.

---

**Versión:** 1.0.0
**Última actualización:** 2025-11-01
**Estado:** Producción (Educational Use Only)

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub
