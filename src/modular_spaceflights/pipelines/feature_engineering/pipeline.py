"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.17.5
"""

from kedro.pipeline import Pipeline, node

from modular_spaceflights.pipelines.feature_engineering.nodes import (
    feature_maker,
    joiner,
)


def create_feature_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=feature_maker,
                inputs=["prm_table", "params:feature_type"],
                outputs="feature_table",
            )
        ]
    )


def create_joining_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=joiner,
                inputs=[
                    "spine_table",
                    "static_features",
                    "feature_1",
                    "feature_2",
                ],
                outputs="model_input_table",
            )
        ]
    )
