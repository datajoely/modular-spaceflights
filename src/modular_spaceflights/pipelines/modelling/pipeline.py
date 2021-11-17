from typing import List
from kedro.pipeline import Pipeline, node, pipeline
from functools import reduce
from operator import add

from .nodes import evaluate_model, split_data, train_model


def create_split_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=split_data,
                inputs=["model_input_table", "parameters"],
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split_data",
            )
        ]
    )


def create_train_evaluate_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=train_model,
                inputs=["X_train", "y_train", "params:dummy_model_options"],
                outputs=["regressor", "model_params"],
                name="train_model",
            ),
            node(
                func=evaluate_model,
                inputs=["regressor", "X_test", "y_test"],
                outputs="r2_score",
                name="evaluate_model",
            ),
        ]
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
