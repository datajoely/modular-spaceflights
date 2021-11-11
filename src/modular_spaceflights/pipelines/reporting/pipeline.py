"""
This is a boilerplate pipeline 'reporting'
generated using Kedro 0.17.5
"""

from kedro.pipeline import Pipeline, node

from modular_spaceflights.pipelines.reporting.nodes import generate_reports


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=generate_reports,
                inputs=["model_input_table"],
                outputs=[
                    "price_histogram",
                    "cancellation_policy_breakdown",
                ],
            )
        ]
    )
