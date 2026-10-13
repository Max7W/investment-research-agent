
import pandas as pd
import pytest

from src.backtest import backtest, run_backtest


@pytest.fixture
def sample_data():
    dates = pd.bdate_range("2020-01-01", periods=5)

    prices = pd.DataFrame(
        {
            "Open": [100, 102, 104, 103, 105],
            "Close": [101, 103, 102, 104, 106],
        },
        index=dates,
    )

    signal = pd.Series(
        [1, 1, 0, 1, 0],
        index=dates,
    )

    return prices, signal


def test_new_and_old_interfaces_match(sample_data):
    prices, signal = sample_data

    old_result = backtest(prices, signal)

    new_result = run_backtest(prices, signal)

    pd.testing.assert_frame_equal(
        old_result,
        new_result.history,
    )


def test_final_state_matches_last_history_row(sample_data):
    prices, signal = sample_data

    result = run_backtest(prices, signal)

    last_row = result.history.iloc[-1]
    state = result.final_state

    assert state.cash == pytest.approx(
        last_row["Cash"]
    )

    assert state.shares == pytest.approx(
        last_row["Shares"]
    )

    assert state.last_equity == pytest.approx(
        last_row["Equity"]
    )


def test_new_interface_supports_continuation(sample_data):
    prices, signal = sample_data

    first = run_backtest(
        prices.iloc[:3],
        signal.iloc[:3],
    )

    second = run_backtest(
        prices.iloc[3:],
        signal.iloc[3:],
        initial_state=first.final_state,
        initial_target=int(signal.iloc[2]),
    )

    full = run_backtest(prices, signal)

    combined = pd.concat([
        first.history,
        second.history,
    ])

    pd.testing.assert_frame_equal(
        combined,
        full.history,
    )

    assert second.final_state.last_equity == pytest.approx(
        full.final_state.last_equity
    )
