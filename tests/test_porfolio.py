
import pytest

from src.portfolio import PortfolioState


def test_portfolio_initialization():
    state = PortfolioState(
        cash=100_000,
        shares=0.0,
        last_equity=100_000,
    )

    assert state.cash == 100_000
    assert state.shares == 0.0
    assert state.last_equity == 100_000


def test_portfolio_equity_calculation():
    state = PortfolioState(
        cash=2_000,
        shares=500,
        last_equity=98_000,
    )

    equity = state.equity(close_price=200)

    assert equity == pytest.approx(102_000)


def test_portfolio_state_can_be_updated():
    state = PortfolioState(
        cash=100_000,
        shares=0.0,
        last_equity=100_000,
    )

    state.cash = 50_000
    state.shares = 250

    assert state.equity(200) == pytest.approx(100_000)


import pandas as pd
import pytest

from src.backtest import backtest
from src.portfolio import PortfolioState


def test_backtest_preserves_input_state():
    dates = pd.bdate_range("2020-01-01", periods=3)

    prices = pd.DataFrame(
        {
            "Open": [100.0, 110.0, 120.0],
            "Close": [105.0, 115.0, 125.0],
        },
        index=dates,
    )

    signal = pd.Series([1, 1, 1], index=dates)

    initial_state = PortfolioState(
        cash=0.0,
        shares=10.0,
        last_equity=1_000.0,
    )

    result = backtest(
        prices,
        signal,
        initial_state=initial_state,
        initial_target=1,
    )

    assert initial_state.cash == 0.0
    assert initial_state.shares == 10.0
    assert initial_state.last_equity == 1_000.0

    assert result["Equity"].iloc[0] == pytest.approx(1_050)
    assert result["Return"].iloc[0] == pytest.approx(0.05)
