"""
Technical indicators calculator using pandas-ta
"""
import pandas as pd
import pandas_ta as ta
from typing import List, Dict, Any, Optional
from ..market_data import AlphaVantageClient


class IndicatorCalculator:
    """Calculator for technical indicators"""

    def __init__(self):
        self.market_client = AlphaVantageClient()

    def _get_data_for_calculation(self, symbol: str, lookback_days: int = 200) -> pd.DataFrame:
        """Get historical data for indicator calculation"""
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')

        df = self.market_client.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='daily'
        )

        return df

    def calculate_trend_indicators(
        self,
        symbol: str,
        indicators: List[str],
        periods: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate trend indicators

        Available indicators:
        - SMA: Simple Moving Average
        - EMA: Exponential Moving Average
        - MACD: Moving Average Convergence Divergence
        - ADX: Average Directional Index
        - AROON: Aroon Indicator
        - PSAR: Parabolic SAR
        - SUPERTREND: Supertrend
        - DEMA: Double Exponential Moving Average

        Args:
            symbol: Stock ticker
            indicators: List of indicator names
            periods: Dictionary with periods for each indicator

        Returns:
            Dictionary with calculated indicators
        """
        if periods is None:
            periods = {}

        df = self._get_data_for_calculation(symbol)
        results = {
            'symbol': symbol,
            'last_updated': df.index[-1].strftime('%Y-%m-%d'),
            'indicators': {}
        }

        for indicator in indicators:
            indicator_upper = indicator.upper()

            try:
                if indicator_upper == 'SMA':
                    period = periods.get('SMA', 20)
                    df[f'SMA_{period}'] = ta.sma(df['Close'], length=period)
                    results['indicators']['SMA'] = {
                        'period': period,
                        'current_value': float(df[f'SMA_{period}'].iloc[-1]),
                        'price': float(df['Close'].iloc[-1]),
                        'signal': 'BUY' if df['Close'].iloc[-1] > df[f'SMA_{period}'].iloc[-1] else 'SELL'
                    }

                elif indicator_upper == 'EMA':
                    period = periods.get('EMA', 20)
                    df[f'EMA_{period}'] = ta.ema(df['Close'], length=period)
                    results['indicators']['EMA'] = {
                        'period': period,
                        'current_value': float(df[f'EMA_{period}'].iloc[-1]),
                        'price': float(df['Close'].iloc[-1]),
                        'signal': 'BUY' if df['Close'].iloc[-1] > df[f'EMA_{period}'].iloc[-1] else 'SELL'
                    }

                elif indicator_upper == 'MACD':
                    macd_data = ta.macd(df['Close'], fast=12, slow=26, signal=9)
                    if macd_data is not None:
                        results['indicators']['MACD'] = {
                            'macd': float(macd_data['MACD_12_26_9'].iloc[-1]),
                            'signal': float(macd_data['MACDs_12_26_9'].iloc[-1]),
                            'histogram': float(macd_data['MACDh_12_26_9'].iloc[-1]),
                            'crossover': 'BULLISH' if macd_data['MACD_12_26_9'].iloc[-1] > macd_data['MACDs_12_26_9'].iloc[-1] else 'BEARISH'
                        }

                elif indicator_upper == 'ADX':
                    period = periods.get('ADX', 14)
                    adx_data = ta.adx(df['High'], df['Low'], df['Close'], length=period)
                    if adx_data is not None:
                        adx_value = float(adx_data[f'ADX_{period}'].iloc[-1])
                        results['indicators']['ADX'] = {
                            'period': period,
                            'adx': adx_value,
                            'plus_di': float(adx_data[f'DMP_{period}'].iloc[-1]),
                            'minus_di': float(adx_data[f'DMN_{period}'].iloc[-1]),
                            'trend_strength': 'STRONG' if adx_value > 25 else 'WEAK' if adx_value < 20 else 'MODERATE'
                        }

                elif indicator_upper == 'AROON':
                    period = periods.get('AROON', 25)
                    aroon_data = ta.aroon(df['High'], df['Low'], length=period)
                    if aroon_data is not None:
                        results['indicators']['AROON'] = {
                            'period': period,
                            'aroon_up': float(aroon_data[f'AROONU_{period}'].iloc[-1]),
                            'aroon_down': float(aroon_data[f'AROOND_{period}'].iloc[-1]),
                            'signal': 'BULLISH' if aroon_data[f'AROONU_{period}'].iloc[-1] > aroon_data[f'AROOND_{period}'].iloc[-1] else 'BEARISH'
                        }

                elif indicator_upper == 'PSAR':
                    psar_data = ta.psar(df['High'], df['Low'], df['Close'])
                    if psar_data is not None:
                        current_price = float(df['Close'].iloc[-1])
                        psar_value = float(psar_data['PSARl_0.02_0.2'].iloc[-1]) if pd.notna(psar_data['PSARl_0.02_0.2'].iloc[-1]) else float(psar_data['PSARs_0.02_0.2'].iloc[-1])
                        results['indicators']['PSAR'] = {
                            'value': psar_value,
                            'price': current_price,
                            'signal': 'BUY' if current_price > psar_value else 'SELL'
                        }

                elif indicator_upper == 'SUPERTREND':
                    period = periods.get('SUPERTREND', 10)
                    supertrend_data = ta.supertrend(df['High'], df['Low'], df['Close'], length=period, multiplier=3)
                    if supertrend_data is not None:
                        results['indicators']['SUPERTREND'] = {
                            'period': period,
                            'value': float(supertrend_data[f'SUPERT_{period}_3.0'].iloc[-1]),
                            'direction': int(supertrend_data[f'SUPERTd_{period}_3.0'].iloc[-1]),
                            'signal': 'BUY' if supertrend_data[f'SUPERTd_{period}_3.0'].iloc[-1] == 1 else 'SELL'
                        }

                elif indicator_upper == 'DEMA':
                    period = periods.get('DEMA', 20)
                    df[f'DEMA_{period}'] = ta.dema(df['Close'], length=period)
                    results['indicators']['DEMA'] = {
                        'period': period,
                        'current_value': float(df[f'DEMA_{period}'].iloc[-1]),
                        'price': float(df['Close'].iloc[-1]),
                        'signal': 'BUY' if df['Close'].iloc[-1] > df[f'DEMA_{period}'].iloc[-1] else 'SELL'
                    }

            except Exception as e:
                results['indicators'][indicator] = {
                    'error': str(e)
                }

        return results

    def calculate_momentum_indicators(
        self,
        symbol: str,
        indicators: List[str],
        periods: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate momentum indicators

        Available indicators:
        - RSI: Relative Strength Index
        - STOCH: Stochastic Oscillator
        - CCI: Commodity Channel Index
        - WILLR: Williams %R
        - ROC: Rate of Change
        - MFI: Money Flow Index
        - TSI: True Strength Index
        - MOM: Momentum

        Args:
            symbol: Stock ticker
            indicators: List of indicator names
            periods: Dictionary with periods for each indicator

        Returns:
            Dictionary with calculated indicators
        """
        if periods is None:
            periods = {}

        df = self._get_data_for_calculation(symbol)
        results = {
            'symbol': symbol,
            'last_updated': df.index[-1].strftime('%Y-%m-%d'),
            'indicators': {}
        }

        for indicator in indicators:
            indicator_upper = indicator.upper()

            try:
                if indicator_upper == 'RSI':
                    period = periods.get('RSI', 14)
                    df[f'RSI_{period}'] = ta.rsi(df['Close'], length=period)
                    rsi_value = float(df[f'RSI_{period}'].iloc[-1])
                    results['indicators']['RSI'] = {
                        'period': period,
                        'value': rsi_value,
                        'signal': 'OVERSOLD' if rsi_value < 30 else 'OVERBOUGHT' if rsi_value > 70 else 'NEUTRAL',
                        'interpretation': 'Strong BUY' if rsi_value < 30 else 'Strong SELL' if rsi_value > 70 else 'HOLD'
                    }

                elif indicator_upper == 'STOCH' or indicator_upper == 'STOCHASTIC':
                    k_period = periods.get('STOCH_K', 14)
                    d_period = periods.get('STOCH_D', 3)
                    stoch_data = ta.stoch(df['High'], df['Low'], df['Close'], k=k_period, d=d_period)
                    if stoch_data is not None:
                        k_value = float(stoch_data[f'STOCHk_{k_period}_{d_period}_3'].iloc[-1])
                        d_value = float(stoch_data[f'STOCHd_{k_period}_{d_period}_3'].iloc[-1])
                        results['indicators']['STOCHASTIC'] = {
                            'k_period': k_period,
                            'd_period': d_period,
                            'k_value': k_value,
                            'd_value': d_value,
                            'signal': 'OVERSOLD' if k_value < 20 else 'OVERBOUGHT' if k_value > 80 else 'NEUTRAL'
                        }

                elif indicator_upper == 'CCI':
                    period = periods.get('CCI', 20)
                    df[f'CCI_{period}'] = ta.cci(df['High'], df['Low'], df['Close'], length=period)
                    cci_value = float(df[f'CCI_{period}'].iloc[-1])
                    results['indicators']['CCI'] = {
                        'period': period,
                        'value': cci_value,
                        'signal': 'OVERSOLD' if cci_value < -100 else 'OVERBOUGHT' if cci_value > 100 else 'NEUTRAL'
                    }

                elif indicator_upper == 'WILLR':
                    period = periods.get('WILLR', 14)
                    df[f'WILLR_{period}'] = ta.willr(df['High'], df['Low'], df['Close'], length=period)
                    willr_value = float(df[f'WILLR_{period}'].iloc[-1])
                    results['indicators']['WILLR'] = {
                        'period': period,
                        'value': willr_value,
                        'signal': 'OVERSOLD' if willr_value < -80 else 'OVERBOUGHT' if willr_value > -20 else 'NEUTRAL'
                    }

                elif indicator_upper == 'ROC':
                    period = periods.get('ROC', 10)
                    df[f'ROC_{period}'] = ta.roc(df['Close'], length=period)
                    roc_value = float(df[f'ROC_{period}'].iloc[-1])
                    results['indicators']['ROC'] = {
                        'period': period,
                        'value': roc_value,
                        'signal': 'BULLISH' if roc_value > 0 else 'BEARISH'
                    }

                elif indicator_upper == 'MFI':
                    period = periods.get('MFI', 14)
                    df[f'MFI_{period}'] = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=period)
                    mfi_value = float(df[f'MFI_{period}'].iloc[-1])
                    results['indicators']['MFI'] = {
                        'period': period,
                        'value': mfi_value,
                        'signal': 'OVERSOLD' if mfi_value < 20 else 'OVERBOUGHT' if mfi_value > 80 else 'NEUTRAL'
                    }

                elif indicator_upper == 'TSI':
                    fast = periods.get('TSI_FAST', 13)
                    slow = periods.get('TSI_SLOW', 25)
                    tsi_data = ta.tsi(df['Close'], fast=fast, slow=slow)
                    if tsi_data is not None:
                        tsi_value = float(tsi_data[f'TSI_{fast}_{slow}_13'].iloc[-1])
                        results['indicators']['TSI'] = {
                            'fast': fast,
                            'slow': slow,
                            'value': tsi_value,
                            'signal': 'BULLISH' if tsi_value > 0 else 'BEARISH'
                        }

                elif indicator_upper == 'MOM' or indicator_upper == 'MOMENTUM':
                    period = periods.get('MOM', 10)
                    df[f'MOM_{period}'] = ta.mom(df['Close'], length=period)
                    mom_value = float(df[f'MOM_{period}'].iloc[-1])
                    results['indicators']['MOMENTUM'] = {
                        'period': period,
                        'value': mom_value,
                        'signal': 'BULLISH' if mom_value > 0 else 'BEARISH'
                    }

            except Exception as e:
                results['indicators'][indicator] = {
                    'error': str(e)
                }

        return results

    def calculate_volatility_indicators(
        self,
        symbol: str,
        indicators: List[str],
        periods: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate volatility indicators

        Available indicators:
        - BBANDS: Bollinger Bands
        - ATR: Average True Range
        - KC: Keltner Channels
        - STDDEV: Standard Deviation
        - DONCHIAN: Donchian Channels
        - UI: Ulcer Index

        Args:
            symbol: Stock ticker
            indicators: List of indicator names
            periods: Dictionary with periods for each indicator

        Returns:
            Dictionary with calculated indicators
        """
        if periods is None:
            periods = {}

        df = self._get_data_for_calculation(symbol)
        results = {
            'symbol': symbol,
            'last_updated': df.index[-1].strftime('%Y-%m-%d'),
            'indicators': {}
        }

        for indicator in indicators:
            indicator_upper = indicator.upper()

            try:
                if indicator_upper == 'BBANDS' or indicator_upper == 'BB':
                    period = periods.get('BBANDS', 20)
                    std = periods.get('BBANDS_STD', 2)
                    bbands = ta.bbands(df['Close'], length=period, std=std)
                    if bbands is not None:
                        current_price = float(df['Close'].iloc[-1])
                        upper = float(bbands[f'BBU_{period}_{std}.0'].iloc[-1])
                        middle = float(bbands[f'BBM_{period}_{std}.0'].iloc[-1])
                        lower = float(bbands[f'BBL_{period}_{std}.0'].iloc[-1])

                        results['indicators']['BBANDS'] = {
                            'period': period,
                            'std': std,
                            'upper_band': upper,
                            'middle_band': middle,
                            'lower_band': lower,
                            'current_price': current_price,
                            'bandwidth': upper - lower,
                            'signal': 'OVERBOUGHT' if current_price > upper else 'OVERSOLD' if current_price < lower else 'NEUTRAL'
                        }

                elif indicator_upper == 'ATR':
                    period = periods.get('ATR', 14)
                    df[f'ATR_{period}'] = ta.atr(df['High'], df['Low'], df['Close'], length=period)
                    atr_value = float(df[f'ATR_{period}'].iloc[-1])
                    results['indicators']['ATR'] = {
                        'period': period,
                        'value': atr_value,
                        'interpretation': 'High volatility' if atr_value > df[f'ATR_{period}'].mean() else 'Low volatility'
                    }

                elif indicator_upper == 'KC' or indicator_upper == 'KELTNER':
                    period = periods.get('KC', 20)
                    kc = ta.kc(df['High'], df['Low'], df['Close'], length=period)
                    if kc is not None:
                        current_price = float(df['Close'].iloc[-1])
                        upper = float(kc[f'KCUe_{period}_2'].iloc[-1])
                        middle = float(kc[f'KCBe_{period}_2'].iloc[-1])
                        lower = float(kc[f'KCLe_{period}_2'].iloc[-1])

                        results['indicators']['KELTNER'] = {
                            'period': period,
                            'upper_channel': upper,
                            'middle_channel': middle,
                            'lower_channel': lower,
                            'current_price': current_price,
                            'signal': 'OVERBOUGHT' if current_price > upper else 'OVERSOLD' if current_price < lower else 'NEUTRAL'
                        }

                elif indicator_upper == 'STDDEV' or indicator_upper == 'STDEV':
                    period = periods.get('STDDEV', 20)
                    df[f'STDDEV_{period}'] = ta.stdev(df['Close'], length=period)
                    stddev_value = float(df[f'STDDEV_{period}'].iloc[-1])
                    results['indicators']['STDDEV'] = {
                        'period': period,
                        'value': stddev_value,
                        'interpretation': 'High volatility' if stddev_value > df[f'STDDEV_{period}'].mean() else 'Low volatility'
                    }

                elif indicator_upper == 'DONCHIAN' or indicator_upper == 'DC':
                    period = periods.get('DONCHIAN', 20)
                    donchian = ta.donchian(df['High'], df['Low'], lower_length=period, upper_length=period)
                    if donchian is not None:
                        current_price = float(df['Close'].iloc[-1])
                        upper = float(donchian[f'DCU_{period}_{period}'].iloc[-1])
                        middle = float(donchian[f'DCM_{period}_{period}'].iloc[-1])
                        lower = float(donchian[f'DCL_{period}_{period}'].iloc[-1])

                        results['indicators']['DONCHIAN'] = {
                            'period': period,
                            'upper_channel': upper,
                            'middle_channel': middle,
                            'lower_channel': lower,
                            'current_price': current_price,
                            'signal': 'BREAKOUT_UP' if current_price >= upper else 'BREAKOUT_DOWN' if current_price <= lower else 'NEUTRAL'
                        }

                elif indicator_upper == 'UI' or indicator_upper == 'ULCER':
                    period = periods.get('UI', 14)
                    df[f'UI_{period}'] = ta.ui(df['Close'], length=period)
                    ui_value = float(df[f'UI_{period}'].iloc[-1])
                    results['indicators']['ULCER'] = {
                        'period': period,
                        'value': ui_value,
                        'interpretation': 'High risk/drawdown' if ui_value > df[f'UI_{period}'].mean() else 'Low risk/drawdown'
                    }

            except Exception as e:
                results['indicators'][indicator] = {
                    'error': str(e)
                }

        return results

    def calculate_volume_indicators(
        self,
        symbol: str,
        indicators: List[str],
        periods: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate volume indicators

        Available indicators:
        - OBV: On Balance Volume
        - VWAP: Volume Weighted Average Price
        - AD: Accumulation/Distribution
        - CMF: Chaikin Money Flow
        - VO: Volume Oscillator
        - PVT: Price Volume Trend

        Args:
            symbol: Stock ticker
            indicators: List of indicator names
            periods: Dictionary with periods for each indicator

        Returns:
            Dictionary with calculated indicators
        """
        if periods is None:
            periods = {}

        df = self._get_data_for_calculation(symbol)
        results = {
            'symbol': symbol,
            'last_updated': df.index[-1].strftime('%Y-%m-%d'),
            'indicators': {}
        }

        for indicator in indicators:
            indicator_upper = indicator.upper()

            try:
                if indicator_upper == 'OBV':
                    df['OBV'] = ta.obv(df['Close'], df['Volume'])
                    obv_value = float(df['OBV'].iloc[-1])
                    obv_prev = float(df['OBV'].iloc[-2])
                    results['indicators']['OBV'] = {
                        'value': obv_value,
                        'change': obv_value - obv_prev,
                        'signal': 'BULLISH' if obv_value > obv_prev else 'BEARISH'
                    }

                elif indicator_upper == 'VWAP':
                    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
                    vwap_value = float(df['VWAP'].iloc[-1])
                    current_price = float(df['Close'].iloc[-1])
                    results['indicators']['VWAP'] = {
                        'value': vwap_value,
                        'current_price': current_price,
                        'signal': 'ABOVE_VWAP' if current_price > vwap_value else 'BELOW_VWAP'
                    }

                elif indicator_upper == 'AD':
                    df['AD'] = ta.ad(df['High'], df['Low'], df['Close'], df['Volume'])
                    ad_value = float(df['AD'].iloc[-1])
                    ad_prev = float(df['AD'].iloc[-2])
                    results['indicators']['AD'] = {
                        'value': ad_value,
                        'change': ad_value - ad_prev,
                        'signal': 'ACCUMULATION' if ad_value > ad_prev else 'DISTRIBUTION'
                    }

                elif indicator_upper == 'CMF':
                    period = periods.get('CMF', 20)
                    df[f'CMF_{period}'] = ta.cmf(df['High'], df['Low'], df['Close'], df['Volume'], length=period)
                    cmf_value = float(df[f'CMF_{period}'].iloc[-1])
                    results['indicators']['CMF'] = {
                        'period': period,
                        'value': cmf_value,
                        'signal': 'BUYING_PRESSURE' if cmf_value > 0 else 'SELLING_PRESSURE'
                    }

                elif indicator_upper == 'VO':
                    fast = periods.get('VO_FAST', 5)
                    slow = periods.get('VO_SLOW', 10)
                    df['VO'] = ((df['Volume'].rolling(window=fast).mean() -
                                 df['Volume'].rolling(window=slow).mean()) /
                                df['Volume'].rolling(window=slow).mean()) * 100
                    vo_value = float(df['VO'].iloc[-1])
                    results['indicators']['VO'] = {
                        'fast': fast,
                        'slow': slow,
                        'value': vo_value,
                        'signal': 'INCREASING_VOLUME' if vo_value > 0 else 'DECREASING_VOLUME'
                    }

                elif indicator_upper == 'PVT':
                    df['PVT'] = ta.pvt(df['Close'], df['Volume'])
                    pvt_value = float(df['PVT'].iloc[-1])
                    pvt_prev = float(df['PVT'].iloc[-2])
                    results['indicators']['PVT'] = {
                        'value': pvt_value,
                        'change': pvt_value - pvt_prev,
                        'signal': 'BULLISH' if pvt_value > pvt_prev else 'BEARISH'
                    }

            except Exception as e:
                results['indicators'][indicator] = {
                    'error': str(e)
                }

        return results
