"""Project pipelines."""
from functools import reduce
from operator import add
from typing import Dict, List

from kedro.pipeline import Pipeline, pipeline

from modular_spaceflights.pipelines import data_ingestion as di
from modular_spaceflights.pipelines import feature_engineering as fe
from modular_spaceflights.pipelines import modelling as mod
from modular_spaceflights.pipelines import reporting as rep


def new_ingestion_pipeline(raw_pipeline: Pipeline) -> Pipeline:
    """[summary]

    Args:
        raw_pipeline (Pipeline): [description]

    Returns:
        Pipeline: [description]
    """
    return pipeline(
        raw_pipeline,
        namespace="data_ingestion",  # provide inputs
        inputs={"reviews", "shuttles", "companies"},  # map inputs outside of namespace
        outputs={
            "prm_spine_table",
            "prm_shuttle_company_reviews",
        },
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


def new_train_eval_pipeline(
    template_model_pipeline: Pipeline, model_type: str
) -> Pipeline:
    """[summary]

    Args:
        template_model_pipeline (Pipeline): [description]
        model_type (str): [description]

    Returns:
        Pipeline: [description]
    """
    return pipeline(
        template_model_pipeline,
        parameters={"params:dummy_model_options": f"params:model_options.{model_type}"},
        inputs=[
            "X_train",
            "X_test",
            "y_train",
            "y_test",
        ],
        outputs={
            "model_params": f"hyperparams_{model_type}",
            "r2_score": f"r2_score_{model_type}",
        },
        namespace=f"{model_type}",
    )


def new_modeling_pipeline(
    split_pipeline: Pipeline, tain_eval_template: Pipeline, model_types: List[str]
) -> Pipeline:

    training_test_references = ["X_train", "X_test", "y_train", "y_test"]

    split_stage_pipeline = pipeline(
        split_pipeline,
        inputs="model_input_table",
        outputs=training_test_references,
    )

    model_pipelines = [
        new_train_eval_pipeline(tain_eval_template, model) for model in model_types
    ]
    all_model_pipelines = pipeline(
        reduce(add, model_pipelines),
        namespace="train_evaluation",
        inputs=training_test_references,
    )

    complete_model_pipeline = split_stage_pipeline + all_model_pipelines
    return complete_model_pipeline


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """
    ingestion_pipeline = new_ingestion_pipeline(di.create_pipeline())

    feature_pipeline = new_feature_eng_pipeline(
        template_feature_pipeline=fe.create_feature_pipeline(),
        combination_pipeline=fe.create_joining_pipeline(),
        metrics=["scaling", "weighting"],
    )

    modelling_pipeline = new_modeling_pipeline(
        split_pipeline=mod.create_split_pipeline(),
        tain_eval_template=mod.create_train_evaluate_pipeline(),
        model_types=["linear_regression", "random_forest"],
    )

    reporting_pipeline = pipeline(
        rep.create_pipeline(), inputs=["model_input_table"], namespace="reporting"
    )

    return {
        "__default__": (
            ingestion_pipeline
            + feature_pipeline
            + modelling_pipeline
            + reporting_pipeline
        ),
        "Data ingestion": ingestion_pipeline,
        "Modelling stage": modelling_pipeline,
        "Automated feature engineering": feature_pipeline,
        "Reporting stage": reporting_pipeline,
    }
