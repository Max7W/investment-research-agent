
import pandas as pd
import pytest

from src.data_split import temporal_split


def test_temporal_split():
    dates = pd.date_range(
        "2016-01-01",
        "2025-12-31",
        freq="D",
    )

    data = pd.DataFrame(
        {"Close": range(len(dates))},
        index=dates,
    )

    train, validation, test = temporal_split(data)

    assert train.index.max() <= pd.Timestamp(
        "2017-12-31"
    )

    assert validation.index.min() > train.index.max()

    assert validation.index.max() <= pd.Timestamp(
        "2021-12-31"
    )

    assert test.index.min() > validation.index.max()

    assert (
        len(train) + len(validation) + len(test)
        == len(data)
    )


def test_temporal_split_rejects_unsorted_data():
    dates = pd.to_datetime([
        "2020-01-02",
        "2019-01-02",
        "2023-01-02",
    ])

    data = pd.DataFrame(
        {"Close": [100, 101, 102]},
        index=dates,
    )

    with pytest.raises(ValueError):
        temporal_split(data)
