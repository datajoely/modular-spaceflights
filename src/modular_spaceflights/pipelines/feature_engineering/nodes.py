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
    """This method accepts a DataFrame, two columns, a numpy function name
    and then a description of what this function does in order to create a new
    column with this applied.

    Args:
        data (pd.DataFrame): The data to add a new feature column to
        column_a (str): The left operand to the `np_function`
        column_b (str): The right operand to the `np_function`
        np_function (Callable): Any top level numpy function such as `np.sum()`
            or `np.max()`. This is has no safeguards so is potentially unsafe
            and must be used with caution.
        column_descriptor (str): This is used to describe the `new_column_name`

    Returns:
        pd.DataFrame: A new dataframe is returned with an additional column added
    """

    new_column_name = f"feat_{column_a}_{column_descriptor}_{column_b}"
    working_data = data.copy()
    working_data[new_column_name] = np_function(
        working_data[column_a], working_data[column_b]
    )
    return working_data


def feature_maker(data: pd.DataFrame, feature_set: Dict[str, Any]) -> pd.DataFrame:
    """This function retrieves configuration from parameters passed in
    and will iteratively create a new column for every column pair provided.

    Args:
        data (pd.DataFrame): The data to create new feature columns for
        feature_set (Dict[str, Any]): Configuration containing the target
            columns and operations to apply.

    Raises:
        AttributeError: Is raised if a valid numpy method cannot be found

    Returns:
        pd.DataFrame: A data frame with new feature columns introduced
    """

    np_method_string = feature_set.get("np_method")

    if not hasattr(np, np_method_string):
        raise AttributeError(f"Unable find method np.{np_method_string}")

    np_function = getattr(np, np_method_string)
    col_descriptor = feature_set.get("col_descriptor")

    # This could rewritten as reduce, but a for loop is easier to read
    for column_a, column_b in feature_set.get("pairs"):
        data = _create_feature(
            data=data,
            column_a=column_a,
            column_b=column_b,
            np_function=np_function,
            column_descriptor=col_descriptor,
        )

    # Limit to identifiers and new feature columns created
    columns_to_retain = [
        x for x in data.columns if x.startswith("feat_") or x.endswith("_id")
    ]
    return data[columns_to_retain]


def joiner(spine_df: pd.DataFrame, *dfs: pd.DataFrame) -> pd.DataFrame:
    """This function takes an arbitrary number of DataFrames and will
    keep inner-joining them to themselves along any columns suffixed
    with "id". There is an assumption that the tables passed in share
    the same identifiers and grain.

    Args:
        spine_df (pd.DataFrame): The first argument should simply contain
        the identifier columns at the correct grain.
        *dfs (pd.DataFrame): Any subsequent tables are joined to the spine

    Returns:
        pd.DataFrame: A single data-frame where all inputs to this function
            have been inner joined together.
    """
    id_columns = [x for x in spine_df.columns if x.endswith("_id")]

    merged_dfs = reduce(
        lambda df, df2: df.merge(df2, on=id_columns, how="inner"), dfs, spine_df
    )
    # Confirm that the number of rows is unchanged after the operation has completed
    assert spine_df.shape[0] == merged_dfs.shape[0]
    return merged_dfs
