
import numpy as np
import pandas as pd
import pytest

from src.metrics import calculate_metrics


def test_metrics_known_equity():
    # 1. 构造人工账户
    dates = pd.date_range("2025-01-01", periods=4)

    equity = pd.Series(
        [100.0, 120.0, 90.0, 110.0],
        index=dates,
    )

    # 2. 计算每日收益率
    returns = equity.pct_change().fillna(0.0)

    # 3. 构造与 metrics.py 兼容的回测结果
    result = pd.DataFrame({
        "Equity": equity,
        "Return": returns,
        "Shares": [0.0, 1.0, 1.0, 0.0],
        "Trade": [0, 1, 0, 1],
    })

    # 4. 调用待验证函数
    metrics = calculate_metrics(
        result,
        initial_cash=100.0,
    )

    # 5. 检验累计收益率
    assert metrics["total_return"] == pytest.approx(0.10)

    # 6. 检验最大回撤
    assert metrics["max_drawdown"] == pytest.approx(-0.25)

    # 7. 检验 Exposure
    assert metrics["exposure"] == pytest.approx(0.50)

    # 8. 检验交易次数
    assert metrics["trade_count"] == 2

        # 9. 检验波动率
    # 包含第一天相对于初始资金的收益率
    daily_returns = np.array([
        100 / 100 - 1,
        120 / 100 - 1,
        90 / 120 - 1,
        110 / 90 - 1,
    ])

    expected_volatility = (
        np.std(daily_returns, ddof=1)
        * np.sqrt(252)
    )

    assert metrics["volatility"] == pytest.approx(
        expected_volatility
    )

    # 10. 检验零无风险利率的简化 Sharpe
    expected_sharpe = (
        np.mean(daily_returns)
        / np.std(daily_returns, ddof=1)
        * np.sqrt(252)
    )

    assert metrics["sharpe"] == pytest.approx(
        expected_sharpe
    )



def test_metrics_include_first_day_return():
    import numpy as np
    import pandas as pd
    import pytest

    from src.metrics import calculate_metrics

    dates = pd.bdate_range("2020-01-01", periods=4)

    daily_returns = [0.10, 0.00, 0.00, 0.00]

    equity = []
    capital = 100_000.0

    for daily_return in daily_returns:
        capital *= 1.0 + daily_return
        equity.append(capital)

    result = pd.DataFrame(
        {
            "Equity": equity,
            "Return": daily_returns,
            "Shares": [1.0] * 4,
            "Trade": [0] * 4,
        },
        index=dates,
    )

    metrics = calculate_metrics(
        result,
        initial_cash=100_000,
    )

    expected_volatility = (
        pd.Series(daily_returns).std(ddof=1)
        * np.sqrt(252)
    )

    expected_sharpe = (
        np.mean(daily_returns)
        / pd.Series(daily_returns).std(ddof=1)
        * np.sqrt(252)
    )

    assert metrics["volatility"] == pytest.approx(
        expected_volatility
    )

    assert metrics["sharpe"] == pytest.approx(
        expected_sharpe
    )
