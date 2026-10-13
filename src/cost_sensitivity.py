from experiment_logger import save_experiment_metadata
from pathlib import Path
import pandas as pd

from backtest import (
    backtest,
    prepare_prices,
    buy_hold_signal,
    sma_signal,
    momentum_signal,
)
from metrics import calculate_metrics


strategies = [
    ("buy_hold", buy_hold_signal),
    ("sma200", sma_signal),
    ("mom60", momentum_signal),
]

cost_levels = [0, 5, 10, 20]

records = []

for ticker in ("SPY", "QQQ", "IWM"):
    raw = pd.read_csv(
        Path("data/raw") / f"{ticker}_2010_2025.csv",
        index_col=0,
        parse_dates=True,
    )

    prices = prepare_prices(raw)

    for strategy_name, signal_fn in strategies:
        signal = signal_fn(prices)

        for cost in cost_levels:
            result = backtest(
                prices,
                signal,
                initial_cash=100_000,
                cost_bps=cost,
            )

            metrics = calculate_metrics(result)

            records.append({
                "Ticker": ticker,
                "Strategy": strategy_name,
                "Cost_bps": cost,
                "Final_Equity": result["Equity"].iloc[-1],
                "CAGR": metrics["cagr"],
                "Sharpe": metrics["sharpe"],
                "Trades": metrics["trade_count"],
                "Total_Fees": result["Fee"].sum(),
            })


df = pd.DataFrame(records)

print(
    df.to_string(
        index=False,
        formatters={
            "Final_Equity": "{:,.2f}".format,
            "CAGR": "{:.2%}".format,
            "Sharpe": "{:.2f}".format,
            "Total_Fees": "{:,.2f}".format,
        },
    )
)

output_path = Path("results/cost_sensitivity.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

print(f"\nSaved results to: {output_path}")


data_paths = {
    ticker: Path("data/raw") / f"{ticker}_2010_2025.csv"
    for ticker in ("SPY", "QQQ", "IWM")
}

metadata = save_experiment_metadata(
    experiment_name="cost_sensitivity",
    tickers=["SPY", "QQQ", "IWM"],
    strategies=[name for name, _ in strategies],
    cost_levels=cost_levels,
    initial_cash=100_000,
    data_paths=data_paths,
    results_path=output_path,
    metadata_path="results/cost_sensitivity_metadata.json",
)

print(
    "Saved metadata to:",
    "results/cost_sensitivity_metadata.json",
)
