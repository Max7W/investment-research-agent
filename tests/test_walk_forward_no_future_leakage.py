
import pandas as pd

from src.backtest import prepare_prices
from src.walk_forward import (
    DATA_PATH,
    run_continuous_walk_forward,
)


def test_future_prices_do_not_change_past_results():
    raw = pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True,
    )

    prices = prepare_prices(raw)

    # 原始数据下的连续 Walk-Forward
    original = run_continuous_walk_forward(prices)

    # 创建一份独立副本
    modified_prices = prices.copy()

    # 只修改 2020 年及以后的市场数据
    future_mask = (
        modified_prices.index >= pd.Timestamp("2020-01-01")
    )

    modified_prices.loc[
        future_mask,
        ["Open", "Close"],
    ] *= 3.0

    # 使用修改后的数据重新执行整个实验
    modified = run_continuous_walk_forward(
        modified_prices
    )

    # 只比较 2020 年之前的历史结果
    original_past = original.loc[: "2019-12-31"]

    modified_past = modified.loc[: "2019-12-31"]

    # 参数、交易、手续费、资金曲线都必须一致
    pd.testing.assert_frame_equal(
        original_past,
        modified_past,
    )
