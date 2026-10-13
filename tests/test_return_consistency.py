
import pandas as pd
import pytest

from src.backtest import prepare_prices
from src.walk_forward import (
    DATA_PATH,
    INITIAL_CASH,
    run_continuous_walk_forward,
)


def test_continuous_returns_match_equity_changes():
    raw = pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True,
    )

    prices = prepare_prices(raw)

    history = run_continuous_walk_forward(prices)

    equity = history["Equity"]
    recorded_returns = history["Return"]

    # 根据账户价值独立重新计算每日收益率
    expected_returns = equity.pct_change()

    # 第一日相对于初始资金计算
    expected_returns.iloc[0] = (
        equity.iloc[0] / INITIAL_CASH - 1.0
    )

    # 比较整个 2018—2021 连续区间
    pd.testing.assert_series_equal(
        recorded_returns,
        expected_returns,
        check_names=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_returns_are_finite():
    raw = pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True,
    )

    prices = prepare_prices(raw)

    history = run_continuous_walk_forward(prices)

    assert history["Return"].notna().all()

    assert (
        history["Return"]
        .map(lambda x: float("-inf") < x < float("inf"))
        .all()
    )
