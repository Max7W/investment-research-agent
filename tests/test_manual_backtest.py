from src.backtest import prepare_prices
import pandas as pd
import pytest

from src.backtest import backtest


def test_three_day_market():
    # 1. 构造人工市场
    dates = pd.date_range("2025-01-01", periods=3)

    prices = pd.DataFrame(
        {
            "Open": [100, 110, 120],
            "Close": [105, 115, 125],
        },
        index=dates,
    )

    # 2. 收盘后产生的交易信号
    signal = pd.Series([1, 1, 0], index=dates)

    # 3. 运行回测，关闭交易成本
    result = backtest(
        prices,
        signal,
        initial_cash=1000,
        cost_bps=0,
    )

    # 4. 验证 Day 1：没有成交
    assert result["Equity"].iloc[0] == pytest.approx(1000)
    assert result["Shares"].iloc[0] == 0

    # 5. 验证 Day 2：开盘买入
    expected_shares = 1000 / 110

    assert result["Shares"].iloc[1] == pytest.approx(
        expected_shares
    )
    assert result["Equity"].iloc[1] == pytest.approx(
        expected_shares * 115
    )

    # 6. 验证 Day 3：继续持仓
    assert result["Shares"].iloc[2] == pytest.approx(
        expected_shares
    )
    assert result["Equity"].iloc[2] == pytest.approx(
        expected_shares * 125
    )
    assert result["Fee"].sum() == 0


def test_buy_sell_with_fees():
    dates = pd.date_range("2025-01-01", periods=4)

    prices = pd.DataFrame(
        {
            "Open": [100, 100, 120, 110],
            "Close": [100, 110, 115, 105],
        },
        index=dates,
    )

    signal = pd.Series([1, 1, 0, 0], index=dates)

    result = backtest(
        prices,
        signal,
        initial_cash=1000,
        cost_bps=10,
    )

    # 买入时扣除 0.1% 手续费
    shares = 1000 / (100 * 1.001)

    # 卖出时再次扣除 0.1% 手续费
    expected_final = shares * 110 * 0.999

    assert result["Shares"].iloc[0] == 0
    assert result["Shares"].iloc[1] == pytest.approx(shares)

    # Day 3 收盘发出卖出信号，但仍持仓
    assert result["Shares"].iloc[2] == pytest.approx(shares)

    # Day 4 开盘卖出
    assert result["Shares"].iloc[3] == pytest.approx(0)

    assert result["Equity"].iloc[-1] == pytest.approx(
        expected_final
    )


def test_adjusted_prices():
    raw = pd.DataFrame({
        "Open": [100, 110],
        "Close": [105, 115],
        "Adj Close": [84, 92],
    })

    prices = prepare_prices(raw)

    assert prices["Open"].iloc[0] == pytest.approx(80)
    assert prices["Close"].iloc[0] == pytest.approx(84)

    assert prices["Open"].iloc[1] == pytest.approx(88)
    assert prices["Close"].iloc[1] == pytest.approx(92)
