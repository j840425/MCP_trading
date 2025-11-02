"""
Trading signal generator combining technical and fundamental analysis
"""
from typing import Dict, Any, List, Optional
from ..indicators import IndicatorCalculator
from ..news_analysis import SentimentAnalyzer


class SignalGenerator:
    """Generator for trading signals"""

    def __init__(self):
        self.indicator_calculator = IndicatorCalculator()
        self.sentiment_analyzer = SentimentAnalyzer()

    def generate_technical_signal(
        self,
        symbol: str,
        strategy_type: str = "simple",
        indicators_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate trading signal based on technical indicators

        Args:
            symbol: Stock ticker
            strategy_type: "simple" or "compound"
            indicators_config: Configuration for indicators

        Returns:
            Trading signal with BUY/SELL/HOLD recommendation
        """
        if indicators_config is None:
            indicators_config = {}

        if strategy_type == "simple":
            return self._simple_technical_strategy(symbol, indicators_config)
        elif strategy_type == "compound":
            return self._compound_technical_strategy(symbol, indicators_config)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

    def _simple_technical_strategy(
        self,
        symbol: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simple technical strategy using single indicator

        Strategies:
        - RSI oversold/overbought
        - MACD crossover
        - SMA crossover
        - Bollinger Bands breakout
        """
        strategy = config.get('strategy', 'RSI')

        if strategy == 'RSI':
            # RSI Strategy
            momentum = self.indicator_calculator.calculate_momentum_indicators(
                symbol=symbol,
                indicators=['RSI'],
                periods={'RSI': config.get('rsi_period', 14)}
            )

            rsi_data = momentum['indicators']['RSI']
            rsi_value = rsi_data['value']

            if rsi_value < 30:
                signal = 'BUY'
                confidence = min((30 - rsi_value) / 30, 1.0)
                reason = f"RSI is oversold at {rsi_value:.2f} (< 30)"
            elif rsi_value > 70:
                signal = 'SELL'
                confidence = min((rsi_value - 70) / 30, 1.0)
                reason = f"RSI is overbought at {rsi_value:.2f} (> 70)"
            else:
                signal = 'HOLD'
                confidence = abs(rsi_value - 50) / 50
                reason = f"RSI is neutral at {rsi_value:.2f}"

            return {
                'symbol': symbol,
                'strategy': 'RSI',
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'details': rsi_data
            }

        elif strategy == 'MACD':
            # MACD Strategy
            trend = self.indicator_calculator.calculate_trend_indicators(
                symbol=symbol,
                indicators=['MACD']
            )

            macd_data = trend['indicators']['MACD']
            histogram = macd_data['histogram']
            crossover = macd_data['crossover']

            if crossover == 'BULLISH' and histogram > 0:
                signal = 'BUY'
                confidence = min(abs(histogram) / 10, 1.0)
                reason = f"MACD bullish crossover with histogram {histogram:.2f}"
            elif crossover == 'BEARISH' and histogram < 0:
                signal = 'SELL'
                confidence = min(abs(histogram) / 10, 1.0)
                reason = f"MACD bearish crossover with histogram {histogram:.2f}"
            else:
                signal = 'HOLD'
                confidence = 0.3
                reason = "MACD shows no clear crossover signal"

            return {
                'symbol': symbol,
                'strategy': 'MACD',
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'details': macd_data
            }

        elif strategy == 'SMA_CROSS':
            # SMA Crossover Strategy (Golden/Death Cross)
            trend = self.indicator_calculator.calculate_trend_indicators(
                symbol=symbol,
                indicators=['SMA'],
                periods={'SMA': config.get('sma_period', 50)}
            )

            sma_data = trend['indicators']['SMA']
            price = sma_data['price']
            sma_value = sma_data['current_value']

            # Simple price vs SMA comparison
            if price > sma_value * 1.02:  # 2% above SMA
                signal = 'BUY'
                confidence = min((price - sma_value) / sma_value / 0.1, 1.0)
                reason = f"Price ${price:.2f} is above SMA ${sma_value:.2f}"
            elif price < sma_value * 0.98:  # 2% below SMA
                signal = 'SELL'
                confidence = min((sma_value - price) / sma_value / 0.1, 1.0)
                reason = f"Price ${price:.2f} is below SMA ${sma_value:.2f}"
            else:
                signal = 'HOLD'
                confidence = 0.3
                reason = f"Price ${price:.2f} is near SMA ${sma_value:.2f}"

            return {
                'symbol': symbol,
                'strategy': 'SMA_CROSS',
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'details': sma_data
            }

        elif strategy == 'BBANDS':
            # Bollinger Bands Strategy
            volatility = self.indicator_calculator.calculate_volatility_indicators(
                symbol=symbol,
                indicators=['BBANDS'],
                periods={'BBANDS': config.get('bb_period', 20)}
            )

            bb_data = volatility['indicators']['BBANDS']
            price = bb_data['current_price']
            upper = bb_data['upper_band']
            lower = bb_data['lower_band']
            signal_type = bb_data['signal']

            if signal_type == 'OVERSOLD':
                signal = 'BUY'
                confidence = min((lower - price) / lower / 0.05, 1.0)
                reason = f"Price ${price:.2f} below lower band ${lower:.2f}"
            elif signal_type == 'OVERBOUGHT':
                signal = 'SELL'
                confidence = min((price - upper) / upper / 0.05, 1.0)
                reason = f"Price ${price:.2f} above upper band ${upper:.2f}"
            else:
                signal = 'HOLD'
                confidence = 0.3
                reason = f"Price ${price:.2f} within bands"

            return {
                'symbol': symbol,
                'strategy': 'BBANDS',
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'details': bb_data
            }

        else:
            raise ValueError(f"Unknown simple strategy: {strategy}")

    def _compound_technical_strategy(
        self,
        symbol: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compound technical strategy using multiple indicators with weights
        """
        # Default indicators and weights
        indicators_config = config.get('indicators', {
            'RSI': {'weight': 0.3, 'period': 14},
            'MACD': {'weight': 0.3},
            'SMA': {'weight': 0.2, 'period': 50},
            'BBANDS': {'weight': 0.2, 'period': 20}
        })

        signals = []
        total_weight = 0

        # Calculate each indicator signal
        for indicator, params in indicators_config.items():
            weight = params.get('weight', 0.25)

            if indicator == 'RSI':
                result = self._simple_technical_strategy(symbol, {'strategy': 'RSI', 'rsi_period': params.get('period', 14)})
            elif indicator == 'MACD':
                result = self._simple_technical_strategy(symbol, {'strategy': 'MACD'})
            elif indicator == 'SMA':
                result = self._simple_technical_strategy(symbol, {'strategy': 'SMA_CROSS', 'sma_period': params.get('period', 50)})
            elif indicator == 'BBANDS':
                result = self._simple_technical_strategy(symbol, {'strategy': 'BBANDS', 'bb_period': params.get('period', 20)})
            else:
                continue

            signals.append({
                'indicator': indicator,
                'signal': result['signal'],
                'confidence': result['confidence'],
                'weight': weight,
                'reason': result['reason']
            })
            total_weight += weight

        # Calculate weighted signal
        buy_score = 0
        sell_score = 0

        for sig in signals:
            weighted_confidence = sig['confidence'] * sig['weight']

            if sig['signal'] == 'BUY':
                buy_score += weighted_confidence
            elif sig['signal'] == 'SELL':
                sell_score += weighted_confidence

        # Determine final signal
        if buy_score > sell_score and buy_score > 0.3:
            final_signal = 'BUY'
            final_confidence = buy_score / total_weight
        elif sell_score > buy_score and sell_score > 0.3:
            final_signal = 'SELL'
            final_confidence = sell_score / total_weight
        else:
            final_signal = 'HOLD'
            final_confidence = 1 - abs(buy_score - sell_score) / total_weight

        # Generate summary
        buy_indicators = [s['indicator'] for s in signals if s['signal'] == 'BUY']
        sell_indicators = [s['indicator'] for s in signals if s['signal'] == 'SELL']

        summary = f"Buy signals: {', '.join(buy_indicators) if buy_indicators else 'None'}. "
        summary += f"Sell signals: {', '.join(sell_indicators) if sell_indicators else 'None'}."

        return {
            'symbol': symbol,
            'strategy': 'COMPOUND_TECHNICAL',
            'signal': final_signal,
            'confidence': final_confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'summary': summary,
            'indicator_signals': signals
        }

    def generate_fundamental_signal(
        self,
        symbol: str,
        news_count: int = 10,
        threshold: float = 0.15
    ) -> Dict[str, Any]:
        """
        Generate trading signal based on news sentiment

        Args:
            symbol: Stock ticker
            news_count: Number of news articles to analyze
            threshold: Confidence threshold for signal

        Returns:
            Trading signal based on sentiment
        """
        # Analyze news sentiment
        sentiment_result = self.sentiment_analyzer.analyze_news_sentiment(
            symbol=symbol,
            news_limit=news_count
        )

        if 'error' in sentiment_result:
            return {
                'symbol': symbol,
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': f"Could not analyze sentiment: {sentiment_result['error']}",
                'sentiment_data': sentiment_result
            }

        sentiment_score = sentiment_result['sentiment_score']
        overall_sentiment = sentiment_result['overall_sentiment']

        # Generate signal based on sentiment
        if sentiment_score > threshold:
            signal = 'BUY'
            confidence = min(sentiment_score, 1.0)
            reason = f"Positive news sentiment (score: {sentiment_score:.2f})"
        elif sentiment_score < -threshold:
            signal = 'SELL'
            confidence = min(abs(sentiment_score), 1.0)
            reason = f"Negative news sentiment (score: {sentiment_score:.2f})"
        else:
            signal = 'HOLD'
            confidence = 1 - abs(sentiment_score)
            reason = f"Neutral news sentiment (score: {sentiment_score:.2f})"

        return {
            'symbol': symbol,
            'strategy': 'FUNDAMENTAL_SENTIMENT',
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'sentiment_score': sentiment_score,
            'overall_sentiment': overall_sentiment,
            'articles_analyzed': sentiment_result['articles_analyzed'],
            'sentiment_distribution': sentiment_result['sentiment_distribution'],
            'interpretation': sentiment_result['interpretation'],
            'top_articles': sentiment_result['articles'][:5]
        }

    def generate_hybrid_signal(
        self,
        symbol: str,
        technical_weight: float = 0.6,
        fundamental_weight: float = 0.4,
        technical_config: Optional[Dict[str, Any]] = None,
        news_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate hybrid signal combining technical and fundamental analysis

        Args:
            symbol: Stock ticker
            technical_weight: Weight for technical analysis (0-1)
            fundamental_weight: Weight for fundamental analysis (0-1)
            technical_config: Configuration for technical indicators
            news_config: Configuration for news analysis

        Returns:
            Combined trading signal
        """
        # Normalize weights
        total_weight = technical_weight + fundamental_weight
        technical_weight = technical_weight / total_weight
        fundamental_weight = fundamental_weight / total_weight

        if technical_config is None:
            technical_config = {'strategy_type': 'compound'}

        if news_config is None:
            news_config = {'news_count': 10, 'threshold': 0.15}

        # Generate technical signal
        technical_signal = self.generate_technical_signal(
            symbol=symbol,
            strategy_type=technical_config.get('strategy_type', 'compound'),
            indicators_config=technical_config.get('indicators')
        )

        # Generate fundamental signal
        fundamental_signal = self.generate_fundamental_signal(
            symbol=symbol,
            news_count=news_config.get('news_count', 10),
            threshold=news_config.get('threshold', 0.15)
        )

        # Calculate weighted scores
        tech_signal = technical_signal['signal']
        tech_confidence = technical_signal['confidence']
        fund_signal = fundamental_signal['signal']
        fund_confidence = fundamental_signal['confidence']

        # Convert signals to numeric scores
        signal_to_score = {'BUY': 1, 'HOLD': 0, 'SELL': -1}

        tech_score = signal_to_score[tech_signal] * tech_confidence * technical_weight
        fund_score = signal_to_score[fund_signal] * fund_confidence * fundamental_weight

        combined_score = tech_score + fund_score

        # Determine final signal
        if combined_score > 0.2:
            final_signal = 'BUY'
            final_confidence = min(combined_score, 1.0)
        elif combined_score < -0.2:
            final_signal = 'SELL'
            final_confidence = min(abs(combined_score), 1.0)
        else:
            final_signal = 'HOLD'
            final_confidence = 1 - abs(combined_score)

        # Generate recommendations
        recommendations = []

        if tech_signal == fund_signal:
            recommendations.append(f"Strong signal: Both technical and fundamental analysis agree on {final_signal}")
        else:
            recommendations.append(f"Mixed signals: Technical suggests {tech_signal}, fundamental suggests {fund_signal}")

        if final_confidence > 0.7:
            recommendations.append("High confidence signal")
        elif final_confidence < 0.4:
            recommendations.append("Low confidence signal - consider waiting for clearer signals")

        return {
            'symbol': symbol,
            'strategy': 'HYBRID',
            'signal': final_signal,
            'confidence': final_confidence,
            'combined_score': combined_score,
            'technical_analysis': {
                'signal': tech_signal,
                'confidence': tech_confidence,
                'weight': technical_weight,
                'weighted_score': tech_score,
                'details': technical_signal
            },
            'fundamental_analysis': {
                'signal': fund_signal,
                'confidence': fund_confidence,
                'weight': fundamental_weight,
                'weighted_score': fund_score,
                'details': fundamental_signal
            },
            'recommendations': recommendations,
            'summary': f"Combined analysis suggests {final_signal} with {final_confidence:.1%} confidence"
        }
