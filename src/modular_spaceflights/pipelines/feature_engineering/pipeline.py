"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.17.5
"""

from typing import List
from functools import reduce
from operator import add
from kedro.pipeline import Pipeline, node, pipeline

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


def new_feature_eng_pipeline(
    template_feature_pipeline: Pipeline,
    combination_pipeline: Pipeline,
    metrics: List[str],
):
    """[summary]

    Args:
        metrics (list, optional): [description]. Defaults to ["scaling", "weighting"].
    """

    def _new_feature(feature_type: str) -> Pipeline:
        """This method will create a new instance of the feature pipelines with
        correctly named parameters and output catalog target. In this example all
        features use the same primary input table to build automated features.
        """
        feature_pipeline = pipeline(
            template_feature_pipeline,
            inputs={"prm_table": "prm_shuttle_company_reviews"},
            parameters={"params:feature_type": f"params:feature_{feature_type}"},
            outputs={"feature_table": f"feat_{feature_type}_metrics"},
        )
        return feature_pipeline

    # In later version of Kedro you will be able to use sum() when collapsing a
    # in iterable of pipelines into one object, here we use reduce to add them
    # all together
    feature_creation_pipeline = reduce(add, [_new_feature(k) for k in metrics])

    # For every feature pipeline created we create a new feature metric table.
    # This step creates a dictionary that can then be passed to the
    # combine_features_pipeline() instance as inputs
    new_feature_inputs = {
        f"feature_{i+1}": f"feat_{k}_metrics" for i, k in enumerate(metrics)
    }

    # Create combination pipeline and provide the relevant inputs
    join_features_pipeline = pipeline(
        combination_pipeline,
        inputs={
            **{
                "spine_table": "prm_spine_table",
                "static_features": "prm_shuttle_company_reviews",
            },
            **new_feature_inputs,
        },
        outputs="model_input_table",
    )

    # The final step combines all pipelines create in this method under one namespace
    # and declare top level pipeline inputs and outputs
    return pipeline(
        feature_creation_pipeline + join_features_pipeline,
        namespace="feature_engineering",
        inputs=["prm_shuttle_company_reviews", "prm_spine_table"],
        outputs=["model_input_table"],
    )
