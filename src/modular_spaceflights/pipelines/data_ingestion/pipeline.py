from kedro.pipeline import Pipeline, node

from .nodes import (
    aggregate_company_data,
    apply_types_to_companies,
    apply_types_to_reviews,
    apply_types_to_shuttles,
    combine_shuttle_level_information,
    create_spine_table,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=apply_types_to_companies,
                inputs="companies",
                outputs="int_typed_companies",
            ),
            node(
                func=apply_types_to_shuttles,
                inputs="shuttles",
                outputs="int_typed_shuttles",
            ),
            node(
                func=apply_types_to_reviews,
                inputs=["reviews", "params:typing.reviews.columns_as_floats"],
                outputs="int_typed_reviews",
            ),
            node(
                func=aggregate_company_data,
                inputs="int_typed_companies",
                outputs="prm_agg_companies",
                name="company_agg",
            ),
            node(
                func=combine_shuttle_level_information,
                inputs={
                    "shuttles": "int_typed_shuttles",
                    "reviews": "int_typed_reviews",
                    "companies": "prm_agg_companies",
                },
                outputs="prm_shuttle_company_reviews",
                name="combine_step",
            ),
            node(
                func=create_spine_table,
                inputs="prm_shuttle_company_reviews",
                outputs="prm_spine_table",
            ),
        ]
    )
