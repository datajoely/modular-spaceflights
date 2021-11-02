from kedro.pipeline import Pipeline, node

from .nodes import create_model_input_table, preprocess_companies, preprocess_shuttles


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=preprocess_companies,
                inputs="companies",
                outputs="typed_companies",
            ),
            node(
                func=preprocess_shuttles,
                inputs="shuttles",
                outputs="typed_shuttles",
            ),
            node(
                func=create_model_input_table,
                inputs=["typed_shuttles", "typed_companies", "reviews"],
                outputs="model_input_table",
                name="create_model_input_table_node",
            ),
        ]
    )
