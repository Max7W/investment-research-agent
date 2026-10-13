
import pytest

from src.execution import execute_order
from src.portfolio import PortfolioState


def test_execute_buy():
    state = PortfolioState(
        cash=100_000,
        last_equity=100_000,
    )

    result = execute_order(
        state,
        target=1,
        open_price=100,
        cost_bps=5,
    )

    assert result.trade == 1
    assert result.fee > 0
    assert state.shares > 0
    assert state.cash == pytest.approx(0, abs=1e-8)

    # 买入金额与手续费之和等于初始现金
    assert (
        state.shares * 100 + result.fee
        == pytest.approx(100_000)
    )


def test_execute_sell():
    state = PortfolioState(
        cash=0,
        shares=100,
        last_equity=10_000,
    )

    result = execute_order(
        state,
        target=0,
        open_price=110,
        cost_bps=5,
    )

    expected_fee = 100 * 110 * 5 / 10_000

    assert result.trade == 1
    assert result.fee == pytest.approx(expected_fee)
    assert state.shares == 0
    assert state.cash == pytest.approx(
        11_000 - expected_fee
    )


def test_execute_no_trade():
    state = PortfolioState(
        cash=100_000,
        last_equity=100_000,
    )

    result = execute_order(
        state,
        target=0,
        open_price=100,
    )

    assert result.trade == 0
    assert result.fee == 0
    assert state.cash == 100_000
    assert state.shares == 0


def test_execute_invalid_target():
    state = PortfolioState(cash=100_000)

    with pytest.raises(ValueError):
        execute_order(
            state,
            target=2,
            open_price=100,
        )


def test_full_investment_leaves_exactly_zero_cash():
    state = PortfolioState(
        cash=100_000,
        shares=0.0,
        last_equity=100_000,
    )

    execute_order(
        state,
        target=1,
        open_price=102,
        cost_bps=5.0,
    )

    # 满仓买入后，现金应该精确等于零
    assert state.cash == 0.0
    assert state.shares > 0

def test_cagr_uses_trading_day_count():
    import pandas as pd
    import pytest

    from src.metrics import calculate_metrics

    dates = pd.bdate_range("2020-01-01", periods=252)

    result = pd.DataFrame(
        {
            "Equity": [
                100_000 * (1.10 ** ((i + 1) / 252))
                for i in range(252)
            ],
            "Return": [
                1.10 ** (1 / 252) - 1
                for _ in range(252)
            ],
            "Shares": [1.0] * 252,
            "Trade": [0] * 252,
        },
        index=dates,
    )

    metrics = calculate_metrics(
        result,
        initial_cash=100_000,
    )

    assert metrics["cagr"] == pytest.approx(
        0.10,
        abs=1e-10,
    )