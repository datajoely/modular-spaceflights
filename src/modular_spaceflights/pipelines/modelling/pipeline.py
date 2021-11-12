from kedro.pipeline import Pipeline, node

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
