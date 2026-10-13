# Data and Validation Protocol

## 1. Data Sources

Historical daily ETF data were downloaded using `yfinance`.

- Assets: SPY, QQQ, IWM
- Period: 2010-01-04 to 2025-12-31
- Frequency: Daily
- Raw data location: `data/raw/`

The raw datasets contain Open, Close, Adj Close, Dividends, Stock Splits, Volume, and other price fields.

## 2. Data Quality

All three datasets contain 4,024 observations.

Automated checks confirm:

- No duplicate dates
- Chronologically sorted dates
- No missing or non-positive Open, Close, or Adj Close prices
- No missing dividend or stock split values

Recorded dividend events:

| Asset | Dividend events | Split events |
|---|---:|---:|
| SPY | 64 | 0 |
| QQQ | 67 | 0 |
| IWM | 64 | 0 |

Automated checks are implemented in `tests/test_data_quality.py`.

These checks establish basic structural integrity, not independent verification of all historical prices or corporate actions.

## 3. Price Adjustment Assumptions

The backtester uses the following transformations:

- `Adjusted Close = Adj Close`
- `Adjustment Factor = Adj Close / Close`
- `Adjusted Open = Open × Adjustment Factor`

Adjusted Open is a synthetic accounting price, not an actual executable historical market quote.

The approach approximates total-return performance. Cash dividends, reinvestment timing, taxes, and actual share accounting are not modeled separately.

The adjusted-price methodology requires further scrutiny before interpreting results as realistic executable returns.

## 4. Execution Assumptions

- Signals are generated using historical closing prices.
- Orders execute at the next trading day's adjusted opening price.
- The strategy is long-or-cash.
- Transaction costs use a fixed basis-point rate.
- Portfolio state is carried across continuous Walk-Forward evaluation windows.

The model does not separately simulate dynamic bid-ask spreads, market impact, taxes, partial fills, or detailed order execution.

## 5. Research Data Splits

Initial chronological partition:

| Partition | Period | Current interpretation |
|---|---|---|
| Training | 2010–2017 | Development and training |
| Validation | 2018–2021 | Previously inspected development evaluation |
| Previously designated test | 2022–2025 | Previously inspected; not pristine holdout |

The 2018–2021 period has been repeatedly evaluated during Walk-Forward development.

The 2022–2025 period was also inspected during earlier baseline experiments.

Therefore, neither period qualifies as an untouched final confirmation dataset for future theory comparisons.

A future confirmatory experiment must establish an untouched holdout or a preregistered prospective evaluation before examining results.

## 6. Walk-Forward Evaluation

Current experimental configuration:

- Asset: SPY
- Evaluation: 2018–2021
- Candidate SMA windows: 50, 100, 200
- Selection criterion: Training-period Sharpe ratio
- Selection method: Expanding historical training window
- Execution: Previous-close signal, next-open execution
- Transaction cost: 5 basis points
- Portfolio continuity: Maintained across evaluation years

These results are development-stage observations, not independent final confirmation of investment effectiveness.

## 7. Reproducibility

Run commands from the project root.

Run tests:

`python -m pytest -q`

Run Walk-Forward:

`python -m src.walk_forward`

Generate experiment metadata:

`python -m src.walk_forward_metadata`

Current metadata records experiment configuration, Git commit, source-data SHA-256, environment versions, and result file locations.

Direct dependency versions are pinned in `requirements-research.txt`. Transitive dependencies are not fully locked.

A fresh virtual environment successfully installed the specified dependencies and passed all 45 automated tests on the development machine.

## 8. Interpretation Limits

- A simplified SMA implementation does not represent an entire investment theory.
- Backtested performance does not guarantee future returns.
- Future experiments must account for transaction costs, market exposure, look-ahead bias, survivorship bias, data snooping, and multiple testing.
- Theory-guided and unguided evolutionary searches must use comparable search budgets and independent evaluation.
