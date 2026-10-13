
from dataclasses import dataclass

from src.portfolio import PortfolioState


@dataclass(frozen=True)
class ExecutionResult:
    """一次交易执行的结果。"""

    fee: float
    trade: int


def execute_order(
    state: PortfolioState,
    target: int,
    open_price: float,
    cost_bps: float = 5.0,
) -> ExecutionResult:
    """
    按开盘价将账户调整至目标仓位。

    target:
        0 = 持有现金
        1 = 满仓做多

    直接更新传入的 PortfolioState。
    """

    if target not in (0, 1):
        raise ValueError("Target must be 0 or 1")

    if open_price <= 0:
        raise ValueError("Open price must be positive")

    if cost_bps < 0:
        raise ValueError("Transaction cost cannot be negative")

    fee_rate = cost_bps / 10_000

    # 买入：现金账户切换为满仓做多
    if target == 1 and state.shares == 0:
        notional = state.cash / (1 + fee_rate)
        fee = notional * fee_rate

        state.shares = notional / open_price

        # 当前模型为满仓买入，交易后现金理论上恰好为零。
        # 直接设为 0.0，避免浮点舍入产生极小的负现金。
        state.cash = 0.0

        return ExecutionResult(
            fee=fee,
            trade=1,
        )

    # 卖出：满仓做多切换为现金账户
    if target == 0 and state.shares > 0:
        notional = state.shares * open_price
        fee = notional * fee_rate

        state.cash += notional - fee
        state.shares = 0.0

        return ExecutionResult(
            fee=fee,
            trade=1,
        )

    # 目标仓位与当前仓位一致，不交易
    return ExecutionResult(
        fee=0.0,
        trade=0,
    )
