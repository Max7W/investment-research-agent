
from pathlib import Path
import pandas as pd

from backtest import (
    prepare_prices,
    sma_signal,
    momentum_signal,
)

for ticker in ("SPY", "QQQ", "IWM"):
    raw = pd.read_csv(
        Path("data/raw") / f"{ticker}_2010_2025.csv",
        index_col=0,
        parse_dates=True,
    )

    adjusted = prepare_prices(raw)

    for name, fn in [
        ("sma200", sma_signal),
        ("mom60", momentum_signal),
    ]:
        raw_signal = fn(raw)
        adj_signal = fn(adjusted)

        # 排除指标尚未形成的预热期
        warmup = 200 if name == "sma200" else 60

        differences = (
            raw_signal.iloc[warmup:]
            != adj_signal.iloc[warmup:]
        )

        print(
            ticker,
            name,
            "different signal days:",
            int(differences.sum()),
            "of",
            len(differences),
        )
