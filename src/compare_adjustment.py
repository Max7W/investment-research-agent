
from pathlib import Path
import pandas as pd

from backtest import (
    backtest,
    prepare_prices,
    buy_hold_signal,
    sma_signal,
    momentum_signal,
)

strategies = [
    ("buy_hold", buy_hold_signal),
    ("sma200", sma_signal),
    ("mom60", momentum_signal),
]

for ticker in ("SPY", "QQQ", "IWM"):
    raw = pd.read_csv(
        Path("data/raw") / f"{ticker}_2010_2025.csv",
        index_col=0,
        parse_dates=True,
    )

    adjusted = prepare_prices(raw)

    print(f"\n=== {ticker} ===")

    for name, fn in strategies:
        raw_signal = fn(raw)
        adj_signal = fn(adjusted)

        # A: 原始信号 + 原始价格
        result_a = backtest(raw, raw_signal)

        # B: 原始信号 + 调整后价格
        result_b = backtest(adjusted, raw_signal)

        # C: 调整后信号 + 调整后价格
        result_c = backtest(adjusted, adj_signal)

        a = result_a["Equity"].iloc[-1]
        b = result_b["Equity"].iloc[-1]
        c = result_c["Equity"].iloc[-1]

        print(
            f"{name:10s} "
            f"A={a:,.2f}  "
            f"B={b:,.2f}  "
            f"C={c:,.2f}  "
            f"B-A={b-a:+,.2f}  "
            f"C-B={c-b:+,.2f}"
        )
