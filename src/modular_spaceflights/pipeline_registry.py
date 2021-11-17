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
    ingestion_pipeline = di.new_ingestion_pipeline(namespace="data_ingestion")

    feature_pipeline = fe.new_feature_eng_pipeline(metrics=["scaling", "weighting"])

    modelling_pipeline = mod.new_modeling_pipeline(
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
