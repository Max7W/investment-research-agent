
import pandas as pd


def temporal_split(
    data,
    train_end="2017-12-31",
    validation_end="2021-12-31",
):
    """
    按时间划分训练集、验证集和测试集。
    """

    if not isinstance(data.index, pd.DatetimeIndex):
        raise TypeError(
            "Data index must be DatetimeIndex"
        )

    if not data.index.is_monotonic_increasing:
        raise ValueError(
            "Data must be sorted by date"
        )

    if data.index.has_duplicates:
        raise ValueError(
            "Data contains duplicate dates"
        )

    train_end = pd.Timestamp(train_end)
    validation_end = pd.Timestamp(validation_end)

    if train_end >= validation_end:
        raise ValueError(
            "train_end must be earlier than validation_end"
        )

    train = data.loc[
        data.index <= train_end
    ].copy()

    validation = data.loc[
        (data.index > train_end)
        & (data.index <= validation_end)
    ].copy()

    test = data.loc[
        data.index > validation_end
    ].copy()

    if any(
        subset.empty
        for subset in (train, validation, test)
    ):
        raise ValueError(
            "Train, validation and test must be non-empty"
        )

    return train, validation, test
