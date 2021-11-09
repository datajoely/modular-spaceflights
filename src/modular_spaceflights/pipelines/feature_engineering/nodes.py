"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.17.5
"""

from functools import reduce
from typing import Any, Callable, Dict

import numpy as np
import pandas as pd


def _create_feature(
    data: pd.DataFrame,
    column_a: str,
    column_b: str,
    np_function: Callable,
    column_descriptor: str,
) -> pd.DataFrame:
    """[summary]

    Args:
        data (pd.DataFrame): [description]
        column_a (str): [description]
        column_b (str): [description]
        np_function (Callable): [description]
        column_descriptor (str): [description]

    Returns:
        pd.DataFrame: [description]
    """

    new_column_name = f"feat_{column_a}_{column_descriptor}_{column_b}"
    data[new_column_name] = np_function(data[column_a], data[column_b])
    return data


def feature_maker(data: pd.DataFrame, feature_set: Dict[str, Any]) -> pd.DataFrame:
    """[summary]

    Args:
        data (pd.DataFrame): [description]
        feature_set (Dict[str, Any]): [description]

    Raises:
        AttributeError: [description]

    Returns:
        pd.DataFrame: [description]
    """

    np_method_string = feature_set.get("np_method")

    if not hasattr(np, np_method_string):
        raise AttributeError(f"Unable find method np.{np_method_string}")

    np_function = getattr(np, np_method_string)
    col_descriptor = feature_set.get("col_descriptor")

    # could be a reduce
    for column_a, column_b in feature_set.get("pairs"):
        data = _create_feature(
            data=data,
            column_a=column_a,
            column_b=column_b,
            np_function=np_function,
            column_descriptor=col_descriptor,
        )
    columns_to_retain = [
        x for x in data.columns if x.startswith("feat_") or x.endswith("_id")
    ]
    return data[columns_to_retain]


def joiner(*dfs: pd.DataFrame) -> pd.DataFrame:
    """[summary]

    Returns:
        pd.DataFrame: [description]
    """
    iter_dfs = iter(dfs)
    first_df = next(iter_dfs)
    id_columns = [x for x in first_df.columns if x.endswith("_id")]
    merged_dfs = reduce(
        lambda df, df2: df.merge(df2, on=id_columns, how="inner"), iter_dfs, first_df
    )
    assert first_df.shape[0] == merged_dfs.shape[0]
    return merged_dfs
