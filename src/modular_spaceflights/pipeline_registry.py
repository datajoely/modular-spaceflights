
"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline, pipeline

from modular_spaceflights.pipelines import data_ingestion as di
from modular_spaceflights.pipelines import feature_engineering as fe
from modular_spaceflights.pipelines import modelling as mod
from modular_spaceflights.pipelines import reporting as rep


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """
    data_ingestion_pipeline = pipeline(
        di.create_pipeline(),
        namespace="data_ingestion",
        inputs={"reviews", "shuttles", "companies"},
        outputs={"prm_spine_table"},
    )

    feature_engineering_scale_pipeline = pipeline(
        fe.create_feature_pipeline(),
        namespace="feature_engineering.scaling",
        inputs={"prm_table": "prm_spine_table"},
        parameters={"params:feature_type": "params:feature_scale"},
        outputs={"feature_table": "feature_engineering.scaling.feat_scaled_metrics"},
    )

    feature_engineering_weight_pipeline = pipeline(
        fe.create_feature_pipeline(),
        namespace="feature_engineering.weighting",
        inputs={"prm_table": "prm_spine_table"},
        parameters={"params:feature_type": "params:feature_weighting"},
        outputs={
            "feature_table": "feature_engineering.weighting.feat_weighted_metrics"
        },
    )

    feature_join_pipeline = pipeline(
        fe.combine_features_pipeline(),
        inputs={
            "prm_spine_table": "prm_spine_table",
            "feat_weighted_metrics": (
                "feature_engineering.weighting.feat_weighted_metrics"
            ),
            "feat_scaled_metrics": "feature_engineering.scaling.feat_scaled_metrics",
        },
        outputs="model_input_table",
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

    feature_pipeline = (
        feature_engineering_scale_pipeline
        + feature_engineering_weight_pipeline
        + feature_join_pipeline
    )

    modelling_pipeline = splitting_pipeline + model_linear_pipeline + model_rf_pipeline

    reporting_pipeline = rep.create_pipeline()

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
