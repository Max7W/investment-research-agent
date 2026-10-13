
import pandas as pd
import pytest

from src.backtest import backtest
from src.portfolio import PortfolioState


def test_split_backtest_matches_continuous_backtest():
    dates = pd.bdate_range("2020-01-01", periods=10)

    prices = pd.DataFrame(
        {
            "Open": [
                100, 102, 104, 103, 101,
                99, 98, 100, 103, 105,
            ],
            "Close": [
                101, 103, 102, 100, 99,
                97, 101, 102, 104, 106,
            ],
        },
        index=dates,
    )

    # 特意设计跨窗口的买卖信号
    signal = pd.Series(
        [1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
        index=dates,
    )

    # A：一次性完整回测
    full = backtest(
        prices,
        signal,
        initial_cash=100_000,
        cost_bps=5.0,
    )

    # B：第一段 Day 1–5
    first = backtest(
        prices.iloc[:5],
        signal.iloc[:5],
        initial_cash=100_000,
        cost_bps=5.0,
    )

    # 保存第一段结束时的账户状态
    ending_state = PortfolioState(
        cash=float(first["Cash"].iloc[-1]),
        shares=float(first["Shares"].iloc[-1]),
        last_equity=float(first["Equity"].iloc[-1]),
    )

    # 第二段首日必须执行上一段最后一天的信号
    previous_signal = int(signal.iloc[4])

    # B：第二段 Day 6–10
    second = backtest(
        prices.iloc[5:],
        signal.iloc[5:],
        initial_cash=100_000,
        cost_bps=5.0,
        initial_target=previous_signal,
        initial_state=ending_state,
    )

    # 拼接两个窗口的每日结果
    combined = pd.concat([first, second])

    # 每日账户数据都应该一致
    columns = [
        "Equity",
        "Cash",
        "Shares",
        "Fee",
        "Target",
        "Trade",
        "Return",
    ]

    pd.testing.assert_frame_equal(
        full[columns],
        combined[columns],
        check_exact=False,
        rtol=1e-12,
        atol=1e-9,
    )

    # 额外确认：测试确实覆盖了跨窗口交易
    assert second["Trade"].iloc[0] == 1

    # 第二段第一天的收益率也应一致
    assert second["Return"].iloc[0] == pytest.approx(
        full["Return"].iloc[5]
    )
