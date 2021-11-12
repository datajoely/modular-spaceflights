"""
This is a boilerplate pipeline 'reporting'
generated using Kedro 0.17.5
"""

from kedro.pipeline import Pipeline, node

from modular_spaceflights.pipelines.reporting.nodes import (
    make_cancel_policy_chart,
    make_price_histogram,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=make_cancel_policy_chart,
                inputs="model_input_table",
                outputs="cancellation_policy_breakdown",
            ),
            node(
                func=make_price_histogram,
                inputs="model_input_table",
                outputs="price_histogram",
            ),
        ]
    )
