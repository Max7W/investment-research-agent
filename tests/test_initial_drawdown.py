
import pandas as pd
import pytest

from src.metrics import calculate_metrics


def test_drawdown_includes_initial_capital():
    dates = pd.date_range("2025-01-01", periods=3)

    result = pd.DataFrame(
        {
            "Equity": [90000.0, 95000.0, 92000.0],
            "Return": [-0.10, 95000 / 90000 - 1, 92000 / 95000 - 1],
            "Shares": [1.0, 1.0, 1.0],
            "Trade": [1, 0, 0],
        },
        index=dates,
    )

    metrics = calculate_metrics(
        result,
        initial_cash=100000.0,
    )

    assert metrics["max_drawdown"] == pytest.approx(-0.10)
