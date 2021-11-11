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


def combine_features_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=joiner,
                inputs=[
                    "prm_spine_table",
                    "feat_weighted_metrics",
                    "feat_scaled_metrics",
                ],
                outputs="model_input_table",
            )
        ]
    )
