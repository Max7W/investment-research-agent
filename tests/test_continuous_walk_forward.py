
import pandas as pd
import pytest

from src.backtest import prepare_prices
from src.walk_forward import (
    DATA_PATH,
    EVALUATION_YEARS,
    INITIAL_CASH,
    run_continuous_walk_forward,
)


@pytest.fixture(scope="module")
def continuous_data():
    raw = pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True,
    )

    prices = prepare_prices(raw)
    history = run_continuous_walk_forward(prices)

    return prices, history


def test_dates_are_sorted_and_unique(continuous_data):
    prices, history = continuous_data

    assert history.index.is_monotonic_increasing
    assert history.index.is_unique

    expected = prices.loc["2018":"2021"].index

    pd.testing.assert_index_equal(
        history.index,
        expected,
        check_names=False,
    )


def test_year_boundary_returns_are_continuous(continuous_data):
    _, history = continuous_data

    for year in EVALUATION_YEARS[1:]:
        previous_year = history[
            history["Year"] == year - 1
        ]

        current_year = history[
            history["Year"] == year
        ]

        previous_equity = previous_year["Equity"].iloc[-1]
        first_equity = current_year["Equity"].iloc[0]

        actual_return = current_year["Return"].iloc[0]

        expected_return = (
            first_equity / previous_equity - 1.0
        )

        assert actual_return == pytest.approx(
            expected_return,
            abs=1e-12,
        )


def test_daily_accounting_identity(continuous_data):
    prices, history = continuous_data

    aligned_close = prices.loc[
        history.index,
        "Close",
    ]

    calculated_equity = (
        history["Cash"]
        + history["Shares"] * aligned_close
    )

    pd.testing.assert_series_equal(
        history["Equity"],
        calculated_equity,
        check_names=False,
        rtol=1e-12,
        atol=1e-8,
    )


def test_initial_capital_and_positive_equity(continuous_data):
    _, history = continuous_data

    assert INITIAL_CASH > 0
    assert (history["Equity"] > 0).all()

    assert history["Equity"].iloc[0] > 0


def test_selected_window_is_constant_within_year(
    continuous_data,
):
    _, history = continuous_data

    for year in EVALUATION_YEARS:
        annual = history[history["Year"] == year]

        assert not annual.empty

        assert annual["Selected_Window"].nunique() == 1
