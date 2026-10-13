
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")

REQUIRED_COLUMNS = [
    "Date", "Open", "High", "Low",
    "Close", "Adj Close", "Volume",
    "Dividends", "Stock Splits", "Capital Gains"
]


def validate_etf(symbol):
    path = DATA_DIR / f"{symbol}_2010_2025.csv"
    df = pd.read_csv(path, parse_dates=["Date"])

    errors = []

    # 1. 检查必需字段
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        errors.append(f"Missing columns: {missing_cols}")
        return errors

    # 2. 检查缺失值
    if df[REQUIRED_COLUMNS].isna().any().any():
        errors.append("Missing values detected")

    # 3. 检查日期
    if df["Date"].duplicated().any():
        errors.append("Duplicate dates detected")

    if not df["Date"].is_monotonic_increasing:
        errors.append("Dates are not sorted")

    # 4. 检查价格
    prices = df[["Open", "High", "Low", "Close"]]

    if (prices <= 0).any().any():
        errors.append("Non-positive prices detected")

    # 5. 检查 OHLC 逻辑
    invalid_ohlc = (
        (df["High"] < prices.max(axis=1)) |
        (df["Low"] > prices.min(axis=1))
    )

    if invalid_ohlc.any():
        errors.append("Invalid OHLC relationships")

    return errors


if __name__ == "__main__":
    for symbol in ["SPY", "QQQ", "IWM"]:
        errors = validate_etf(symbol)

        if errors:
            print(f"[FAIL] {symbol}")
            for error in errors:
                print("  -", error)
        else:
            print(f"[PASS] {symbol}")
