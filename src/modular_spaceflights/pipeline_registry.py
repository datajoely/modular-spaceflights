"""Project pipelines."""
from typing import Dict, List
from functools import reduce
from operator import add

from kedro.pipeline import Pipeline, pipeline

from modular_spaceflights.pipelines import data_ingestion as di
from modular_spaceflights.pipelines import feature_engineering as fe
from modular_spaceflights.pipelines import modelling as mod
from modular_spaceflights.pipelines import reporting as rep
from modular_spaceflights.pipelines.feature_engineering.pipeline import (
    create_joining_pipeline,
)


def new_ingestion_pipeline(raw_pipeline: Pipeline) -> Pipeline:
    return pipeline(
        raw_pipeline,
        namespace="data_ingestion",  # provide inputs
        inputs={"reviews", "shuttles", "companies"},  # map inputs outside of namespace
        outputs={
            "prm_spine_table",
            "prm_shuttle_company_reviews",
        },
    )


def new_dynamic_feature_pipeline(
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
        correctly named parameters and output catalog target. In this example all features
        use the same primary input table to build automated features.
        """
        feature_pipeline = pipeline(
            template_feature_pipeline,
            inputs={"prm_table": "prm_shuttle_company_reviews"},
            parameters={"params:feature_type": f"params:feature_{feature_type}"},
            outputs={"feature_table": f"feat_{feature_type}_metrics"},
        )
        return feature_pipeline

    # In later version of Kedro you will be able to use sum() when collapsing a
    # in iterable of pipelines into one object, here we use reduce to add them all together
    feature_creation_pipeline = reduce(add, [_new_feature(k) for k in metrics])

    # For every feature pipeline created we create a new feature metric table.
    # This step creates a dictionary that can then be passed to the combine_features_pipeline()
    # instance as inputs
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

    # The final step combines all pipelines create in this method under one namespace and
    # declare top level pipeline inputs and outputs
    return pipeline(
        feature_creation_pipeline + join_features_pipeline,
        namespace="feature_engineering",
        inputs=["prm_shuttle_company_reviews", "prm_spine_table"],
        outputs=["model_input_table"],
    )


def new_modeling_pipeline() -> Pipeline:
    pass


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """
    data_ingestion_pipeline = new_ingestion_pipeline(di.create_pipeline())

    feature_pipeline = new_dynamic_feature_pipeline(
        template_feature_pipeline=fe.create_feature_pipeline(),
        combination_pipeline=fe.create_joining_pipeline(),
        metrics=["scaling", "weighting"],
    )

    splitting_pipeline = mod.create_split_pipeline()

    model_linear_pipeline = pipeline(
        mod.create_train_evaluate_pipeline(),
        parameters={"params:dummy_model_options": "params:model_options.linear"},
        inputs=[
            "X_train",
            "X_test",
            "y_train",
            "y_test",
        ],
        outputs={"model_params": "hyperparams_linear", "r2_score": "r2_score_linear"},
        namespace="data_science.linear_regression",
    )

    model_rf_pipeline = pipeline(
        mod.create_train_evaluate_pipeline(),
        parameters={"params:dummy_model_options": "params:model_options.random_forest"},
        inputs=[
            "X_train",
            "X_test",
            "y_train",
            "y_test",
        ],
        outputs={
            "model_params": "hyperparams_random_forest",
            "r2_score": "r2_score_random_forest",
        },
        namespace="data_science.random_forest",
    )

    modelling_pipeline = splitting_pipeline + model_linear_pipeline + model_rf_pipeline

    reporting_pipeline = pipeline(rep.create_pipeline(), inputs=["model_input_table"], namespace='reporting')

    return {
        "__default__": (
            data_ingestion_pipeline
            + feature_pipeline
            + modelling_pipeline
            + reporting_pipeline
        ),
        "Data ingestion": data_ingestion_pipeline,
        "Modelling stage": modelling_pipeline,
        "Automated feature engineering": feature_pipeline,
        "Reporting stage": reporting_pipeline,
        "Split stage": splitting_pipeline,
    }
