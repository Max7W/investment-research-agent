
import pandas as pd
import pytest

from src.backtest import backtest


def test_initial_target_executes_on_first_open():
    dates = pd.date_range("2025-01-01", periods=3)

    prices = pd.DataFrame(
        {
            "Open": [100.0, 110.0, 120.0],
            "Close": [100.0, 110.0, 120.0],
        },
        index=dates,
    )

    signal = pd.Series([1, 1, 1], index=dates)

    result = backtest(
        prices,
        signal,
        initial_cash=1000.0,
        cost_bps=0.0,
        initial_target=1,
    )

    # 第一天开盘就买入 10 股
    assert result["Shares"].iloc[0] == pytest.approx(10.0)

    # 第一天确实发生交易
    assert result["Trade"].iloc[0] == 1

    # 最后一天收盘，10 股价值 1200
    assert result["Equity"].iloc[-1] == pytest.approx(1200.0)


def test_default_initial_target_remains_zero():
    dates = pd.date_range("2025-01-01", periods=2)

    prices = pd.DataFrame(
        {
            "Open": [100.0, 100.0],
            "Close": [100.0, 100.0],
        },
        index=dates,
    )

    signal = pd.Series([1, 1], index=dates)

    result = backtest(
        prices,
        signal,
        initial_cash=1000.0,
        cost_bps=0.0,
    )

    # 默认第一天不交易，第二天才执行第一天的信号
    assert result["Trade"].tolist() == [0, 1]
