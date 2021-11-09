"""
This is a boilerplate pipeline 'reporting'
generated using Kedro 0.17.5
"""
import pandas as pd


def generate_reports(model_input_table: pd.DataFrame) -> pd.DataFrame:
    """[summary]

    Args:
        model_input_table (pd.DataFrame): [description]
        explicit_features (List[str]): [description]
        target (str): [description]

    Returns:
        [type]: [description]
    """

    cancellation_analysis_df = (
        model_input_table.groupby(["company_location", "cancellation_policy"])["price"]
        .sum()
        .reset_index()
    )
    price_data_df = model_input_table[["price", "engine_type"]]
    return price_data_df, cancellation_analysis_df
