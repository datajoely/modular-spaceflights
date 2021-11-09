# Copyright 2021 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline, pipeline

from modular_spaceflights.pipelines import data_ingestion as di
from modular_spaceflights.pipelines import data_science as ds
from modular_spaceflights.pipelines import feature_engineering as fe
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

    splitting_pipeline = ds.create_split_pipeline()

    model_linear_pipeline = pipeline(
        ds.create_train_evaluate_pipeline(),
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
        ds.create_train_evaluate_pipeline(),
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
