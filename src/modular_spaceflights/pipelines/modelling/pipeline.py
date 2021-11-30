from functools import reduce
from operator import add
from typing import List

from kedro.pipeline import Pipeline, node
from kedro.pipeline.modular_pipeline import pipeline

from .nodes import evaluate_model, split_data, train_model


def create_split_pipeline(X_refs: List[str], y_refs: List[str]) -> Pipeline:
    """This is a simple one node pipeline that accepts a DataFrame
    along with some logic on how to cut up that pipeline which is then
    passed to the underlying sklearn `train_test_split()` method.

    Args:
        X_refs (List[str]): The names of the `X_train` and `X_test` tables
        y_refs (List[str]): The names of the `y_train` and `y_test` tables

    Returns:
        Pipeline: This pipeline returns four outputs corresponding to
            train and test tables needed to evaluate the model performance
    """
    return Pipeline(
        [
            node(
                func=split_data,
                inputs=["model_input_table", "parameters"],
                outputs=X_refs + y_refs,
            )
        ]
    )


def create_train_evaluate_pipeline(
    train_refs: List[str], test_refs: List[str]
) -> Pipeline:
    """This two node pipeline will train a Sklearn model and return
    a regressor object along with `experiment_params` as tracked
    metadata.

    Args:
        train_refs (List[str]): The names of the `X_tain` and `y_train`
            tables
        test_refs (List[str]): The names of the `X_test` and `y_test`
            tables

    Returns:
        Pipeline: This pipeline has been designed in a way that
        allows the user to implement different parametrised Sklearn
        modelling approaches via modular pipeline instances.
    """
    return Pipeline(
        [
            node(
                func=train_model,
                inputs=train_refs + ["params:dummy_model_options"],
                outputs=["regressor", "experiment_params"],
            ),
            node(
                func=evaluate_model,
                inputs=["regressor"] + test_refs,
                outputs="r2_score",
            ),
        ]
    )


def new_train_eval_instance(
    eval_pipeline_template: Pipeline, model_type: str, train_test_refs: List[str]
) -> Pipeline:
    """This method instantiates an modular pipeline instance of the training
    and evaluation pipeline with overrides for the model parameters, tracked
    outputs and namespaces.


    Args:
        eval_pipeline_template (Pipeline): The template pipeline to instantiate
        model_type (str): This is used to retrieve the relevant parameter and
            catalog names. It is also used as the namespace for this pipeline
            instance.
        train_test_refs (List[str]): The names of the train and test data tables

    Returns:
        Pipeline: The full pipeline instantiated for a particular model type.
    """
    return pipeline(
        pipe=eval_pipeline_template,
        parameters={"params:dummy_model_options": f"params:model_options.{model_type}"},
        inputs=train_test_refs,
        outputs={  # both of these are tracked as experiments
            "experiment_params": f"hyperparams_{model_type}",
            "r2_score": f"r2_score_{model_type}",
        },
        namespace=f"{model_type}",
    )


def new_modeling_pipeline(
    model_types: List[str], X_train: str, X_test: str, y_train: str, y_test: str
) -> Pipeline:
    """This function will create a complete modelling
    pipeline that consolidates a single shared 'split' stage,
    several modular instances of the 'train test evaluate' stage
    and returns a single, appropriately namespaced Kedro pipeline
    object:
    ┌───────────────────────────────┐
    │                               │
    │        ┌────────────┐         │
    │     ┌──┤ Split stage├───┐     │
    │     │  └──────┬─────┘   │     │
    │     │         │         │     │
    │ ┌───┴───┐ ┌───┴───┐ ┌───┴───┐ │
    │ │ Model │ │ Model │ │ Model │ │
    │ │ Type  │ │ Type  │ │  Type │ │
    │ │   1   │ │   2   │ │   n.. │ │
    │ └───────┘ └───────┘ └───────┘ │
    │                               │
    └───────────────────────────────┘

    Args:
        model_types (List[str]): The instances of Sklearn models
            we want to build, each of these must correspond to
            patameter keys of the same name

    Returns:
        Pipeline: A single pipeline encapsulating the split
            stage as well as one train/evaluation sub-pipeline
            for each `model_type` passed in.
    """

    lookup = {
        "test_train_refs": [X_train, X_test, y_train, y_test],
        "X_refs": [X_train, X_test],
        "y_refs": [y_train, y_test],
        "train_refs": [X_train, y_train],
        "test_refs": [X_test, y_test],
    }

    # Split the model input data
    split_stage_pipeline = pipeline(
        pipe=create_split_pipeline(X_refs=lookup["X_refs"], y_refs=lookup["y_refs"]),
        inputs="model_input_table",
        outputs=lookup["test_train_refs"],
    )

    # Instantiate a new modeling pipeline for every model type
    model_pipelines = [
        new_train_eval_instance(
            eval_pipeline_template=create_train_evaluate_pipeline(
                train_refs=lookup["train_refs"], test_refs=lookup["test_refs"]
            ),
            model_type=model,
            train_test_refs=lookup["test_train_refs"],
        )
        for model in model_types
    ]

    # Combine modeling pipeliens into one pipeline object
    all_modeling_pipelines = reduce(add, model_pipelines)

    # Namespace consolidated modeling pipelines
    consolidated_model_pipelines = pipeline(
        pipe=all_modeling_pipelines,
        namespace="train_evaluation",
        inputs=lookup["test_train_refs"],
    )

    # Combine split and modeling stages into one pipeline
    complete_model_pipeline = split_stage_pipeline + consolidated_model_pipelines
    return complete_model_pipeline
