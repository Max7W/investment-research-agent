from metrics import calculate_metrics
from pathlib import Path
import pandas as pd

from backtest import (
    backtest,
    buy_hold_signal,
    sma_signal,
    momentum_signal,
    prepare_prices,
)

for ticker in ("SPY", "QQQ", "IWM"):

    raw = pd.read_csv(
        Path("data/raw") / f"{ticker}_2010_2025.csv",
        index_col=0,
        parse_dates=True,
    )

    prices = prepare_prices(raw)

    for name, fn in [
        ("buy_hold", buy_hold_signal),
        ("sma200", sma_signal),
        ("mom60", momentum_signal),
    ]:

        signal = fn(prices)

        result = backtest(prices, signal)

        metrics = calculate_metrics(result)

        print(
            ticker,
            name,
            "final equity:",
            round(result["Equity"].iloc[-1], 2),
            "total fees:",
            round(result["Fee"].sum(), 2),
        )

        
        print(
            "Total Return:", f"{metrics['total_return']:.2%}",
            "CAGR:", f"{metrics['cagr']:.2%}",
            "Volatility:", f"{metrics['volatility']:.2%}",
            "Max Drawdown:", f"{metrics['max_drawdown']:.2%}",
            "Sharpe Ratio:", f"{metrics['sharpe']:.2f}",
            "Exposure:", f"{metrics['exposure']:.2%}",
            "Trades:", metrics["trade_count"],
            )

