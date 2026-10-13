
import pandas as pd
import pytest

from src.backtest import backtest


def test_transaction_cost_round_trip():
    dates = pd.date_range(
        "2025-01-01",
        periods=3,
    )

    prices = pd.DataFrame(
        {
            "Open": [100.0, 100.0, 100.0],
            "Close": [100.0, 100.0, 100.0],
        },
        index=dates,
    )

    # 当天收盘产生信号，次日开盘执行
    signal = pd.Series(
        [1, 0, 0],
        index=dates,
    )

    result = backtest(
        prices,
        signal,
        initial_cash=1000.0,
        cost_bps=100.0,
    )

    expected_equity = 1000.0 * 0.99 / 1.01
    expected_total_fees = 2 * (1000.0 / 1.01) * 0.01

    assert result["Equity"].iloc[-1] == pytest.approx(
        expected_equity
    )

    assert result["Fee"].sum() == pytest.approx(
        expected_total_fees
    )

    assert result["Trade"].tolist() == [0, 1, 1]

    assert result["Shares"].iloc[-1] == pytest.approx(0.0)


def test_zero_transaction_cost():
    dates = pd.date_range(
        "2025-01-01",
        periods=3,
    )

    prices = pd.DataFrame(
        {
            "Open": [100.0, 100.0, 100.0],
            "Close": [100.0, 100.0, 100.0],
        },
        index=dates,
    )

    signal = pd.Series(
        [1, 0, 0],
        index=dates,
    )

    result = backtest(
        prices,
        signal,
        initial_cash=1000.0,
        cost_bps=0.0,
    )

    assert result["Equity"].iloc[-1] == pytest.approx(
        1000.0
    )

    assert result["Fee"].sum() == pytest.approx(0.0)
