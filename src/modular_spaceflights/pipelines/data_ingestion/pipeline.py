from kedro.pipeline import Pipeline, node

from .nodes import (
    combine_shuttle_level_information,
    apply_types_to_companies,
    apply_types_to_shuttles,
    apply_types_to_reviews,
    aggregate_company_data,
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
                tags="domain_level",
                name="combine_step",
            ),
        ]
    )
