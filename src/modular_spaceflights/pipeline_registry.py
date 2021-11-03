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


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """
    data_ingestion_pipeline = pipeline(
        di.create_pipeline(),
        namespace="data_ingestion",
        inputs={"reviews", "shuttles", "companies"},
        outputs={"prm_shuttle_company_reviews"},
    )

    feature_engineering_pipeline = pipeline(
        
    )

    model_linear_pipeline = pipeline(
        ds.create_pipeline(),
        inputs={"model_input_table"},
        parameters={"params:dummy_model_options": "params:model_options.linear"},
        namespace="data_science.linear_regression",
    )
    model_rf_pipeline = pipeline(
        ds.create_pipeline(),
        inputs={"model_input_table"},
        parameters={"params:dummy_model_options": "params:model_options.random_forest"},
        namespace="data_science.random_forest",
    )

    modelling_pipeline = model_linear_pipeline + model_rf_pipeline

    return {
        "__default__": data_ingestion_pipeline + feature_engineering_pipeline +  modelling_pipeline,
        "di": data_ingestion_pipeline,
        "fe": feature_engineering_pipeline,
        "ds": modelling_pipeline,
    }
