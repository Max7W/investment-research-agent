
import pandas as pd

from src.walk_forward import select_best_window


def test_future_prices_cannot_change_selected_window():
    dates = pd.bdate_range(
        "2017-01-02",
        "2018-12-31",
    )

    prices = pd.DataFrame(
        {
            "Open": [
                100.0 + i * 0.05
                for i in range(len(dates))
            ],
            "Close": [
                100.0 + i * 0.05
                for i in range(len(dates))
            ],
        },
        index=dates,
    )

    train_end = "2017-12-31"

    # 原始训练集
    train_original = prices.loc[:train_end]

    selected_original = select_best_window(
        train_original
    )

    # 人为修改 2018 年的全部价格
    modified_prices = prices.copy()

    modified_prices.loc["2018-01-01":, "Open"] = 500.0
    modified_prices.loc["2018-01-01":, "Close"] = 500.0

    # 再次截取训练集
    train_modified = modified_prices.loc[:train_end]

    selected_modified = select_best_window(
        train_modified
    )

    assert selected_original == selected_modified
