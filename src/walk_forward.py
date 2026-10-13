
from pathlib import Path
from src.backtest import buy_hold_signal

import pandas as pd

from src.backtest import (
    prepare_prices,
    sma_signal,
    backtest,
    run_backtest,
)
from src.metrics import calculate_metrics


DATA_PATH = Path("data/raw/SPY_2010_2025.csv")

WINDOWS = [50, 100, 200]
EVALUATION_YEARS = [2018, 2019, 2020, 2021]

INITIAL_CASH = 100_000
COST_BPS = 5.0


def select_best_window(train_prices):
    """
    仅使用传入的训练期价格选择 SMA 参数。
    """

    candidate_scores = []

    for window in WINDOWS:
        train_signal = sma_signal(
            train_prices,
            window=window,
        )

        train_result = backtest(
            train_prices,
            train_signal,
            initial_cash=INITIAL_CASH,
            cost_bps=COST_BPS,
        )

        train_metrics = calculate_metrics(
            train_result,
            initial_cash=INITIAL_CASH,
        )

        candidate_scores.append((
            window,
            train_metrics["sharpe"],
        ))

    best_window = max(
        candidate_scores,
        key=lambda x: (
            float("-inf")
            if pd.isna(x[1])
            else x[1]
        ),
    )[0]

    return best_window


def evaluate_window(prices, window, start, end):
    # 只使用截至当前评估区间结束的价格
    history = prices.loc[:end]

    # 计算 SMA 信号
    signal = sma_signal(history, window=window)

    # 提取实际参与回测的时间区间
    eval_prices = history.loc[start:end]
    eval_signal = signal.loc[start:end]

    if eval_prices.empty:
        raise ValueError("Empty evaluation window")

    # 找到评估期第一个交易日在历史数据中的位置
    first_position = history.index.get_loc(
        eval_prices.index[0]
    )

    if first_position == 0:
        raise ValueError("Insufficient prior history")

    # 评估期开始前最后一个交易日的信号
    initial_target = int(
        signal.iloc[first_position - 1]
    )

    # 从评估期第一天开始建立账户
    result = backtest(
        eval_prices,
        eval_signal,
        initial_cash=INITIAL_CASH,
        cost_bps=COST_BPS,
        initial_target=initial_target,
    )

    return calculate_metrics(
        result,
        initial_cash=INITIAL_CASH,
    )


def run_continuous_walk_forward(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    连续 Walk-Forward 回测。

    每年：
    1. 只使用上一年末及以前的数据选择参数。
    2. 使用新参数计算上一年最后交易日的信号。
    3. 在新年首个交易日开盘执行该信号。
    4. 继承上一年度的现金、持仓和账户价值。
    """

    state = None
    histories = []

    for year in EVALUATION_YEARS:
        train_end = f"{year - 1}-12-31"
        eval_start = f"{year}-01-01"
        eval_end = f"{year}-12-31"

        train_prices = prices.loc[:train_end]

        # 只能使用过去的数据选参数
        best_window = select_best_window(train_prices)

        # 计算信号时保留历史数据，确保 SMA 有足够预热期
        history_prices = prices.loc[:eval_end]

        signal = sma_signal(
            history_prices,
            window=best_window,
        )

        eval_prices = history_prices.loc[
            eval_start:eval_end
        ]

        if eval_prices.empty:
            raise ValueError(
                f"No evaluation data for {year}"
            )

        first_position = history_prices.index.get_loc(
            eval_prices.index[0]
        )

        if first_position == 0:
            raise ValueError(
                "Missing previous trading day"
            )

        # 新年度首日执行上一交易日的信号
        initial_target = int(
            signal.iloc[first_position - 1]
        )

        result = run_backtest(
            prices=eval_prices,
            signal=signal.loc[eval_prices.index],
            initial_cash=INITIAL_CASH,
            cost_bps=COST_BPS,
            initial_target=initial_target,
            initial_state=state,
        )

        # 下一年继承当前账户
        state = result.final_state

        annual_history = result.history.copy()
        annual_history["Year"] = year
        annual_history["Selected_Window"] = best_window

        histories.append(annual_history)

    return pd.concat(histories)


def main():
    raw = pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True,
    )

    prices = prepare_prices(raw)

    records = []

    for year in EVALUATION_YEARS:
        train_end = f"{year - 1}-12-31"
        eval_start = f"{year}-01-01"
        eval_end = f"{year}-12-31"

        train_prices = prices.loc[:train_end]

        best_window = select_best_window(train_prices)
        

        eval_metrics = evaluate_window(
            prices,
            window=best_window,
            start=eval_start,
            end=eval_end,
        )

        records.append({
            "Year": year,
            "Selected_Window": best_window,
            "CAGR": eval_metrics["cagr"],
            "Sharpe": eval_metrics["sharpe"],
            "Max_Drawdown": eval_metrics["max_drawdown"],
            "Trades": eval_metrics["trade_count"],
        })

    df = pd.DataFrame(records)

    print(df.to_string(index=False))

    output = Path("results/walk_forward.csv")
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    df.to_csv(output, index=False)

    print(f"\nSaved results to: {output}")

    continuous = run_continuous_walk_forward(prices)

    output = Path("results/walk_forward_equity.csv")

    continuous.to_csv(output)

    continuous = run_continuous_walk_forward(prices)

    output = Path("results/walk_forward_equity.csv")
    continuous.to_csv(output)

    # ===== Experiment 018: Buy & Hold Benchmark =====

    benchmark_prices = prices.loc[
        continuous.index.min():continuous.index.max()
    ]

    benchmark_signal = buy_hold_signal(benchmark_prices)

    benchmark = run_backtest(
        prices=benchmark_prices,
        signal=benchmark_signal,
        initial_cash=INITIAL_CASH,
        cost_bps=COST_BPS,
        initial_target=1,
    )

    benchmark_output = Path(
        "results/walk_forward_benchmark.csv"
    )

    benchmark.history.to_csv(benchmark_output)

    print("\nExperiment 018: Final Equity")
    print(f"Walk-Forward SMA: ${continuous['Equity'].iloc[-1]:,.2f}")
    print(f"Buy & Hold SPY:  ${benchmark.history['Equity'].iloc[-1]:,.2f}")

    print("\nContinuous Walk-Forward:")
    print(continuous.tail())

    print(f"\nSaved continuous equity to: {output}")

    # ===== Experiment 018: Performance Comparison =====

    sma_metrics = calculate_metrics(
        continuous,
        initial_cash=INITIAL_CASH,
    )

    benchmark_metrics = calculate_metrics(
        benchmark.history,
        initial_cash=INITIAL_CASH,
    )

    comparison = pd.DataFrame(
        {
            "Walk-Forward SMA": sma_metrics,
            "SPY Buy & Hold": benchmark_metrics,
        }
    )

    # 额外统计累计交易手续费
    comparison.loc[
        "total_fees"
    ] = [
        continuous["Fee"].sum(),
        benchmark.history["Fee"].sum(),
    ]

    print("\nExperiment 018: Performance Comparison")
    print(comparison.to_string())

    comparison_output = Path(
        "results/walk_forward_comparison.csv"
    )

    comparison.to_csv(comparison_output)

    print(
        f"\nSaved comparison to: {comparison_output}"
    )


if __name__ == "__main__":
    main()
