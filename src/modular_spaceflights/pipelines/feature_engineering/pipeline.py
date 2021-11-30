"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.17.5
"""

from functools import reduce
from operator import add
from typing import Iterable, List

from kedro.pipeline import Pipeline, node
from kedro.pipeline.modular_pipeline import pipeline

from modular_spaceflights.pipelines.feature_engineering.nodes import (
    feature_maker,
    joiner,
)


def _create_feat_template_pipeline(**kwargs) -> Pipeline:
    """This function instantiates a single node pipeline
    which is designed to be overridden with dynamic inputs.
    The inputs and outputs declared are all placeholders that
    do not refer to specific catalog entries, but will be replaced
    using the `pipeline(inputs={}, outputs={}, parameters={})` syntax.

    Returns:
        Pipeline: A template pipeline which will have inputs
        outputs overridden by the `_new_feature()` method.
    """
    return Pipeline(
        [
            node(
                func=feature_maker,
                inputs=["prm_table", "params:feature_type"],
                outputs="feature_table",
            )
        ]
    )


def _new_feature_set(feature_type: str) -> Pipeline:
    """This function will create a set of features by creating an
    instance of the feature template pipeline with appropriately named
    outputs driven by parameters of the same name.

    It is an assumption in this project that all features of this type
    will be working off the `prm_shuttles_company_reviews` table, but this
    could be made dynamic as well.

    Args:
        feature_type (str): This refers to the top level parameter prefixed
            with `feature_...` that contains arguments needed to drive the
            `feature_maker()` method, the key part of the template pipeline.

    Returns:
        Pipeline: This returns an instance of the template feature pipline
        set up to read the correctly named parameters and outputs.
    """

    feature_pipeline = pipeline(
        pipe=_create_feat_template_pipeline(),
        inputs={"prm_table": "prm_shuttle_company_reviews"},
        parameters={"params:feature_type": f"params:feature_{feature_type}"},
        outputs={"feature_table": f"feat_{feature_type}_metrics"},
    )
    return feature_pipeline


def _new_feature_maker_instances(metrics: List[str]) -> Pipeline:
    """This function accepts a list of metrics and instantiates
    an new feature pipeline for each metric provided.

    Args:
        metrics (List[str]): The list of metrics to create. This must
            map to parameters linked under the same name.

    Returns:
        Pipeline: A combined pipeline made up of sub-pipelines created
            for each metric
    """

    new_features_list = [_new_feature_set(k) for k in metrics]

    # We want to add these new pipelines into a single pipeline
    # You can do this manually by doing Pipeline1 + Pipeline 2
    # The reduce function accumulates the list and keeps `add()`ing
    # them together.
    consolidate_feature_pipelines = reduce(add, new_features_list)

    # In a future version of Kedro we will support sum() function
    # to make this cleaner.
    return consolidate_feature_pipelines


def create_joining_pipeline(num_additional_feature_sets: int) -> Pipeline:
    """This function is intended to show how to instantiate a pipeline
    of arbitrary length dynamically.

    In this project we have two tables that
    were created in the ingestion pipeline that will be combined at this
    stage, there are an arbitrary number of `create_feat_template_pipeline()`
    instances and this method caters for that via the `num_additional_features`
    parameter.

    Args:
        num_additional_features (int): The number of additional input columns
            to create. If say 2 is provided as an input we will append two new
            columns `['feature_1', 'feature_2']` to the `joiner()` method. These
            names are again placeholders that will be overridden in modular
            pipeline instances.

    Returns:
        Pipeline: A Pipeline object that has been instantiated with the correct
            number of inputs in created as part of the feature engineering stage.
    """

    additional_features = [f"feature_{i+1}" for i in range(num_additional_feature_sets)]

    return Pipeline(
        [
            node(
                func=joiner,
                inputs=["spine_table", "static_features"] + additional_features,
                outputs="model_input_table",
            )
        ]
    )


def new_feature_eng_pipeline(
    metrics: Iterable[str] = ("scaling", "weighting"),
) -> Pipeline:
    """This function will create the end to end feature engineering pipeline
    and also create the single `model_input` table as an output.

    This pipeline joins together the primary layer tables already ready for
    modelling and will dynamically create and join new feature tables defined by
    the `metrics` parameter.

    Args:
        metrics (List[str]): The list of metrics which features are dynamically
            created against

    Returns:
        Pipeline: A consoildated pipeline that creates all features and produces
            a single model input table.
    """

    # Create dynamic features and consoilidate into single pipeline
    dynamic_features_pipeline = _new_feature_maker_instances(metrics)

    # Get ready to join everything together
    # Map inputs to keys in `conf/base/parameters/feature_engineering.yml`
    # feature_1 <- metric[0] <- e.g. params:feature_scaling
    placeholder_override = {
        f"feature_{i+1}": f"feat_{k}_metrics" for i, k in enumerate(metrics)
    }

    # Create single dictionary with static inputs as well as any metric provided
    # as an argument to this function
    pipeline_inputs_map = {
        **{
            "spine_table": "prm_spine_table",
            "static_features": "prm_shuttle_company_reviews",
        },
        **placeholder_override,
    }

    # Create a table that joins all tables created up until this point
    join_features_pipeline = pipeline(
        create_joining_pipeline(num_additional_feature_sets=len(metrics)),
        inputs=pipeline_inputs_map,
        outputs="model_input_table",
    )

    # Consolidate the feature creation pipeline and joining steps
    # under one namespace
    return pipeline(
        pipe=dynamic_features_pipeline + join_features_pipeline,
        namespace="feature_engineering",
        inputs=["prm_shuttle_company_reviews", "prm_spine_table"],
        outputs=["model_input_table"],
    )
