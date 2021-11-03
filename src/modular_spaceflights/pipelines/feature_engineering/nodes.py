# Copyright 2021 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.17.5
"""

from typing import Callable, Dict, Any
import pandas as pd
import numpy as np
from functools import reduce


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
            column_descriptor=col_descriptor
        )
    columns_to_retain = [x for x in data.columns if x.startswith('feat_') or x.endswith('_id')]
    return data[columns_to_retain]

def joiner(*dfs:pd.DataFrame) -> pd.DataFrame:
    """[summary]

    Returns:
        pd.DataFrame: [description]
    """
    iter_dfs = iter(dfs)
    first_df = next(iter_dfs)
    id_columns = [x for x in first_df.columns if x.endswith('_id')]
    merged_dfs = reduce(lambda df, df2: df.merge(df2, on=id_columns, how='inner'), iter_dfs, first_df)
    assert first_df.shape[0] == merged_dfs.shape[0]
    return merged_dfs