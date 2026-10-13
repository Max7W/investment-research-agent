
import pandas as pd

from src.backtest import sma_signal, momentum_signal


def test_sma_signal_does_not_use_future_prices():
    dates = pd.date_range("2025-01-01", periods=20)

    prices = pd.DataFrame(
        {
            "Open": [100.0 + i for i in range(20)],
            "Close": [100.0 + i for i in range(20)],
        },
        index=dates,
    )

    # 原始数据产生的信号
    original_signal = sma_signal(prices, window=5)

    # 修改第 11 天及之后的价格
    modified_prices = prices.copy()
    modified_prices.loc[dates[10]:, "Close"] = 500.0

    modified_signal = sma_signal(
        modified_prices,
        window=5,
    )

    # 第 10 天及之前的信号必须完全一致
    pd.testing.assert_series_equal(
        original_signal.iloc[:10],
        modified_signal.iloc[:10],
    )


def test_momentum_signal_does_not_use_future_prices():
    dates = pd.date_range("2025-01-01", periods=20)

    prices = pd.DataFrame(
        {
            "Open": [100.0 + i for i in range(20)],
            "Close": [100.0 + i for i in range(20)],
        },
        index=dates,
    )

    original_signal = momentum_signal(
        prices,
        lookback=5,
    )

    modified_prices = prices.copy()
    modified_prices.loc[dates[10]:, "Close"] = 500.0

    modified_signal = momentum_signal(
        modified_prices,
        lookback=5,
    )

    pd.testing.assert_series_equal(
        original_signal.iloc[:10],
        modified_signal.iloc[:10],
    )
