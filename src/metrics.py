
import numpy as np
import pandas as pd


def calculate_metrics(
    result: pd.DataFrame,
    initial_cash: float = 100_000,
) -> dict:

    equity = result["Equity"]
    returns = result["Return"]

    # 累计收益率
    total_return = equity.iloc[-1] / initial_cash - 1

        # CAGR：按每年252个交易日进行年化
    n_days = len(result)

    cagr = (
        (equity.iloc[-1] / initial_cash) ** (252 / n_days) - 1.0
        if n_days > 0 and equity.iloc[-1] > 0
        else np.nan
    )

        # 回测引擎已计算首日收益率，因此保留所有有效交易日
    daily_returns = returns.dropna()

    # 年化波动率：252 个交易日近似一年
    volatility = daily_returns.std(ddof=1) * np.sqrt(252)

    daily_std = daily_returns.std(ddof=1)

    if pd.notna(daily_std) and daily_std > 0:
        sharpe = (
            daily_returns.mean()
            / daily_std
            * np.sqrt(252)
        )
    else:
        sharpe = np.nan

    # 最大回撤
    # 初始资金也应当是计算回撤的基准
    running_max = equity.cummax().clip(lower=initial_cash)

    drawdown = equity / running_max - 1.0

    max_drawdown = drawdown.min()

    # 持有 ETF 的交易日比例
    exposure = (result["Shares"] > 0).mean()

    trade_count = int(result["Trade"].sum())

    return {
        "total_return": total_return,
        "cagr": cagr,
        "volatility": volatility,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "exposure": exposure,
        "trade_count": trade_count,
    }
