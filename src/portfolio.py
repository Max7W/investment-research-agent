
from dataclasses import dataclass


@dataclass
class PortfolioState:
    """
    当前投资账户的状态。

    cash:
        当前持有的现金。

    shares:
        当前持有的股票数量。
        允许小数股。

    last_equity:
        上一个交易日收盘时的账户总价值。
        用于计算跨窗口第一天的收益率。
    """

    cash: float
    shares: float = 0.0
    last_equity: float | None = None

    def equity(self, close_price: float) -> float:
        """按照当前收盘价格计算账户总价值。"""
        return self.cash + self.shares * close_price
