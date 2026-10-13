
import pandas as pd

from src.backtest import backtest


def test_trade_count():
    dates = pd.date_range("2025-01-01", periods=5)

    prices = pd.DataFrame(
        {
            "Open": [100, 100, 100, 100, 100],
            "Close": [100, 100, 100, 100, 100],
        },
        index=dates,
    )

    # 当天收盘产生信号，下一天开盘执行
    signal = pd.Series([1, 1, 0, 0, 0], index=dates)

    result = backtest(
        prices,
        signal,
        initial_cash=1000,
        cost_bps=0,
    )

    # 第 2 天买入，第 4 天卖出
    expected = [0, 1, 0, 1, 0]

    assert result["Trade"].tolist() == expected
    assert result["Trade"].sum() == 2
    assert result["Shares"].iloc[-1] == 0
