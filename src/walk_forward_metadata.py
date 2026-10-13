
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.walk_forward import (
    DATA_PATH,
    WINDOWS,
    EVALUATION_YEARS,
    INITIAL_CASH,
    COST_BPS,
)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def get_git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main():
    output_path = Path(
        "results/walk_forward_metadata.json"
    )
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "experiment": "continuous_walk_forward_sma",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "ticker": "SPY",
        "data_file": str(DATA_PATH),
        "data_sha256": sha256_file(DATA_PATH),
        "initial_cash": INITIAL_CASH,
        "cost_bps": COST_BPS,
        "candidate_windows": WINDOWS,
        "evaluation_years": EVALUATION_YEARS,
        "selection_metric": "sharpe",
        "selection_method": "expanding_window",
        "execution": "previous_close_signal_next_open",
        "annualization_days": 252,
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "git_commit": get_git_commit(),
        "results": [
            "results/walk_forward.csv",
            "results/walk_forward_equity.csv",
            "results/walk_forward_benchmark.csv",
            "results/walk_forward_comparison.csv",
        ],
    }

    output_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved metadata to: {output_path}"
    )


if __name__ == "__main__":
    main()

