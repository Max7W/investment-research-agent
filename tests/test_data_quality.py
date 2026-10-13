
from pathlib import Path

import pandas as pd
import pytest


TICKERS = ["SPY", "QQQ", "IWM"]

DATA_DIR = Path("data/raw")

REQUIRED_COLUMNS = [
    "Open",
    "Close",
    "Adj Close",
    "Dividends",
    "Stock Splits",
]


@pytest.mark.parametrize("ticker", TICKERS)
def test_raw_data_quality(ticker):
    path = DATA_DIR / f"{ticker}_2010_2025.csv"

    assert path.exists(), f"Missing data file: {path}"

    df = pd.read_csv(
        path,
        index_col="Date",
        parse_dates=True,
    )

    # 1. 数据非空
    assert not df.empty

    # 2. 必需字段完整
    assert set(REQUIRED_COLUMNS).issubset(df.columns)

    # 3. 日期有效、唯一且升序
    assert not df.index.hasnans
    assert df.index.is_unique
    assert df.index.is_monotonic_increasing

    # 4. 数据覆盖预期时间范围
    assert df.index.min() == pd.Timestamp("2010-01-04")
    assert df.index.max() == pd.Timestamp("2025-12-31")

    # 5. 关键价格无缺失、无非正值
    prices = df[["Open", "Close", "Adj Close"]]

    assert prices.notna().all().all()
    assert (prices > 0).all().all()

    # 6. 分红与拆股事件无缺失
    assert df[["Dividends", "Stock Splits"]].notna().all().all()

    # 7. 分红和拆股数据不应为负数
    assert (df["Dividends"] >= 0).all()
    assert (df["Stock Splits"] >= 0).all()
