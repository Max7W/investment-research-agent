
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def calculate_file_hash(file_path):
    """计算文件的 SHA-256 哈希值。"""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_git_commit():
    """获取当前 Git commit。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def save_experiment_metadata(
    experiment_name,
    tickers,
    strategies,
    cost_levels,
    initial_cash,
    data_paths,
    results_path,
    metadata_path,
):
    """保存一次实验的参数、环境和数据摘要。"""

    data_hashes = {
        ticker: calculate_file_hash(data_paths[ticker])
        for ticker in tickers
    }

    metadata = {
        "experiment": experiment_name,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "initial_cash": initial_cash,
        "tickers": tickers,
        "strategies": strategies,
        "cost_levels_bps": cost_levels,
        "data_hashes": data_hashes,
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "git_commit": get_git_commit(),
        "results_file": str(results_path),
    }

    metadata_path = Path(metadata_path)
    metadata_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(
            metadata,
            f,
            indent=2,
            ensure_ascii=False,
        )

    return metadata
