
import pandas as pd
import pytest

from src.backtest import backtest


def test_first_day_return_includes_intraday_profit():
    dates = pd.date_range("2025-01-01", periods=2)

    prices = pd.DataFrame(
        {
            "Open": [100.0, 110.0],
            "Close": [110.0, 110.0],
        },
        index=dates,
    )

    signal = pd.Series([1, 1], index=dates)

    result = backtest(
        prices,
        signal,
        initial_cash=1000.0,
        cost_bps=0.0,
        initial_target=1,
    )

    assert result['Equity'].iloc[0] == pytest.approx(1100.0)
    assert result['Return'].iloc[0] == pytest.approx(0.10)


def test_first_day_return_includes_transaction_cost():
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
        cost_bps=100.0,
        initial_target=1,
    )

    expected_return = 1.0 / 1.01 - 1.0

    assert result['Return'].iloc[0] == pytest.approx(
        expected_return
    )
