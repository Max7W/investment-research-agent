# Investment Research Agent

**Computational Discovery and Empirical Evaluation of Investment Theories**

An AI-assisted research project investigating how natural-language investment theories can be transformed into testable hypotheses, executable strategies, and reproducible empirical evaluations.

**Current status: Phase 0 MVP completed.**

This repository is a research infrastructure prototype, not a validated trading system or a source of investment recommendations.

## Research Roadmap

- **Phase 0 — Backtesting & Validation:** Build and test a reproducible backtesting and evaluation infrastructure. MVP completed.
- **Phase 1 — Theory to Strategy:** Extract investment-theory claims, formalize hypotheses, and generate executable strategies.
- **Phase 2 — Theory-Guided Evolution:** Compare theory-guided and unguided evolutionary searches under matched computational budgets.
- **Future Extensions:** Theory fusion, artificial markets, counterfactual price formation, and reflexivity.

## Phase 0 Features

- Daily long-or-cash backtesting
- Previous-close signals with next-open execution
- Simplified proportional transaction costs
- Buy-and-hold, SMA, and momentum baselines
- Portfolio state continuity
- CAGR, volatility, Sharpe ratio, maximum drawdown, exposure, and trade-count metrics
- Expanding-window Walk-Forward evaluation
- Data quality checks for SPY, QQQ, and IWM
- Experiment metadata, Git version tracking, and data SHA-256 recording
- 45 passing automated tests in the verified development environment

## Project Structure

```text
src/                 Backtesting, strategies, metrics, experiments
tests/               Automated tests
data/raw/            Historical ETF data snapshots
results/             Experiment outputs and metadata
requirements.txt     General dependencies
requirements-research.txt
                     Verified direct dependency versions
DATA_AND_VALIDATION.md
                     Data assumptions and validation protocol
```

## Environment Setup

Verified development environment: Python 3.14.7 on Windows.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-research.txt
```

Run commands from the repository root.

## Data Preparation

Historical daily data are retrieved using Yahoo Finance through `yfinance`.

Assets: SPY, QQQ, IWM.

Historical period: 2010–2025.

```powershell
python -m src.download
```

The download script refuses to overwrite existing raw CSV files.

Downloaded data may differ from the original research snapshots due to upstream revisions. Exact reproduction of previously recorded numerical results requires the original data snapshot or verification of matching data hashes.

## Running Tests

```powershell
python -m pytest -q
```

The existing data-quality tests expect the historical CSV files to be present under `data/raw/`.

## Running Walk-Forward Evaluation

```powershell
python -m src.walk_forward
python -m src.walk_forward_metadata
```

The current experiment evaluates an expanding-window SMA selection procedure on SPY over 2018–2021.

## Important Research Limitations

The backtester uses synthetic adjusted opening prices derived from Yahoo Finance adjusted closing prices. These are accounting approximations, not directly executable market prices.

Cash dividends, taxes, dynamic spreads, detailed market impact, and actual share accounting are not modeled separately.

The 2018–2021 evaluation period and the previously designated 2022–2025 test period have already been inspected during development. Neither should be represented as a pristine, untouched final confirmation dataset.

A successful backtest does not establish a general investment theory or guarantee future returns.

See `DATA_AND_VALIDATION.md` for the complete data and validation protocol.

## Research Principles

- Separate original theory claims from LLM interpretations and strategy implementations.
- Prevent look-ahead bias, data snooping, and uncontrolled multiple testing.
- Use comparable search budgets and multiple random seeds in evolutionary experiments.
- Report risk, transaction costs, robustness, and benchmarks alongside returns.
- Preserve reproducibility through versioned code, data provenance, and experiment logs.
