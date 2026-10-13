
"""Minimal long-or-cash, next-open execution backtester.

Supports consistently adjusted OHLC prices for approximate
total-return backtesting.

Adjusted shares are synthetic accounting units, not actual ETF shares.
Dividends are not separately credited.
"""

from dataclasses import dataclass
import math

import pandas as pd

from src.portfolio import PortfolioState
from src.execution import execute_order


@dataclass
class BacktestResult:
    """
    回测结果。

    history:
        每个交易日的账户记录。

    final_state:
        最后一个交易日收盘后的账户状态。
        可用于下一个回测窗口。
    """

    history: pd.DataFrame
    final_state: PortfolioState


def prepare_prices(raw: pd.DataFrame) -> pd.DataFrame:
    """Prepare consistently adjusted Open and Close prices."""

    required = ["Open", "Close", "Adj Close"]

    if not set(required).issubset(raw.columns):
        raise ValueError("Missing required price columns")

    if raw[required].isna().any().any():
        raise ValueError("Missing price values")

    if (raw[required] <= 0).any().any():
        raise ValueError("Prices must be positive")

    factor = raw["Adj Close"] / raw["Close"]

    prices = pd.DataFrame(index=raw.index)

    prices["Open"] = raw["Open"] * factor
    prices["Close"] = raw["Adj Close"]

    return prices


def buy_hold_signal(prices: pd.DataFrame) -> pd.Series:
    return pd.Series(1, index=prices.index, dtype=int)


def sma_signal(
    prices: pd.DataFrame,
    window: int = 200,
) -> pd.Series:
    sma = prices["Close"].rolling(
        window,
        min_periods=window,
    ).mean()

    return (prices["Close"] > sma).astype(int)


def momentum_signal(
    prices: pd.DataFrame,
    lookback: int = 60,
) -> pd.Series:
    return (
        prices["Close"].pct_change(lookback) > 0
    ).astype(int)


def run_backtest(
    prices: pd.DataFrame,
    signal: pd.Series,
    initial_cash: float = 100_000,
    cost_bps: float = 5.0,
    initial_target: int = 0,
    initial_state: PortfolioState | None = None,
) -> BacktestResult:
    """
    执行回测，返回每日记录和最终账户状态。

    第 t 天收盘产生的信号在第 t+1 天开盘执行。

    initial_target:
        第一个交易日开盘前已知的目标仓位。

    initial_state:
        如果提供，则继承上一窗口的账户状态。
        传入对象不会被修改。
    """

    # 1. 输入检查
    if prices.empty:
        raise ValueError("Prices cannot be empty")

    if (
        not prices.index.is_monotonic_increasing
        or prices.index.has_duplicates
    ):
        raise ValueError("Index must be sorted and unique")

    if not prices[["Open", "Close"]].notna().all().all():
        raise ValueError("Missing prices")

    if (prices[["Open", "Close"]] <= 0).any().any():
        raise ValueError("Prices must be positive")

    if (
        not math.isfinite(float(initial_cash))
        or initial_cash <= 0
        or not math.isfinite(float(cost_bps))
        or cost_bps < 0
    ):
        raise ValueError("Invalid cost or capital")

    if initial_target not in (0, 1):
        raise ValueError("Initial target must be 0 or 1")

    signal = signal.reindex(prices.index)

    if signal.isna().any() or not signal.isin([0, 1]).all():
        raise ValueError("Signal must be aligned and binary")

    # 2. 初始化或继承账户状态
    if initial_state is None:
        state = PortfolioState(
            cash=float(initial_cash),
            shares=0.0,
            last_equity=float(initial_cash),
        )
    else:
        # 复制状态，防止修改调用者持有的对象
        state = PortfolioState(
            cash=float(initial_state.cash),
            shares=float(initial_state.shares),
            last_equity=initial_state.last_equity,
        )

    if (
        not math.isfinite(state.cash)
        or not math.isfinite(state.shares)
        or state.cash < 0
        or state.shares < 0
    ):
        raise ValueError("Invalid portfolio state")

    if (
        state.last_equity is None
        or not math.isfinite(float(state.last_equity))
        or state.last_equity <= 0
    ):
        raise ValueError("Invalid previous equity")

    # 3. 逐日推进
    records = []

    for i, (date, row) in enumerate(prices.iterrows()):
        op = float(row["Open"])
        cl = float(row["Close"])

        # 只能执行前一交易日收盘已知的信号
        target = (
            int(initial_target)
            if i == 0
            else int(signal.iloc[i - 1])
        )

        execution = execute_order(
            state=state,
            target=target,
            open_price=op,
            cost_bps=cost_bps,
        )

        equity = state.equity(cl)

        daily_return = (
            equity / state.last_equity - 1.0
        )

        records.append((
            date,
            equity,
            state.cash,
            state.shares,
            execution.fee,
            target,
            execution.trade,
            daily_return,
        ))

        # 保存当日收盘账户价值
        state.last_equity = equity

    # 4. 构建回测历史记录
    history = pd.DataFrame(
        records,
        columns=[
            "Date",
            "Equity",
            "Cash",
            "Shares",
            "Fee",
            "Target",
            "Trade",
            "Return",
        ],
    ).set_index("Date")

    # 5. 同时返回历史记录和最终状态
    return BacktestResult(
        history=history,
        final_state=state,
    )


def backtest(
    prices: pd.DataFrame,
    signal: pd.Series,
    initial_cash: float = 100_000,
    cost_bps: float = 5.0,
    initial_target: int = 0,
    initial_state: PortfolioState | None = None,
) -> pd.DataFrame:
    """
    兼容旧接口，只返回每日回测记录。

    内部调用 run_backtest()，
    因此不存在第二套交易执行逻辑。
    """

    result = run_backtest(
        prices=prices,
        signal=signal,
        initial_cash=initial_cash,
        cost_bps=cost_bps,
        initial_target=initial_target,
        initial_state=initial_state,
    )

    return result.history
