import importlib
import logging
from typing import Any, Dict, Tuple, Union

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split


def split_data(data: pd.DataFrame, parameters: Dict) -> Tuple:
    """Splits data into features and targets training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters.yml.
    Returns:
        Split data.
    """
    X = data[parameters["features"]]
    y = data["price"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=parameters["test_size"], random_state=parameters["random_state"]
    )
    return X_train, X_test, y_train, y_test


def train_model(
    X_train: pd.DataFrame, y_train: pd.Series, model_options: Dict[str, Any]
) -> Union[LinearRegression, RandomForestRegressor]:
    """Trains the linear regression model.

    Args:
        X_train: Training data of independent features.
        y_train: Training data for price.

    Returns:
        Trained model.
    """
    module_name = model_options.get("module")
    class_name = model_options.get("class")

    try:
        regressor_class = getattr(importlib.import_module(module_name), class_name)
    except (ModuleNotFoundError, AttributeError):
        raise ImportError(
            f"Cannot import '{module_name}.{class_name}', please check "
            "spelling and installed dependencies."
        )

    regressor_instance = regressor_class(**model_options.get("kwargs"))
    logger = logging.getLogger(__name__)
    logger.info(f"Fitting model of type {type(regressor_instance)}")

    regressor_instance.fit(X_train, y_train)
    return regressor_instance


def evaluate_model(
    regressor: Union[LinearRegression, RandomForestRegressor],
    X_test: pd.DataFrame,
    y_test: pd.Series,
):
    """Calculates and logs the coefficient of determination.

    Args:
        regressor: Trained model.
        X_test: Testing data of independent features.
        y_test: Testing data for price.
    """
    y_pred = regressor.predict(X_test)
    score = r2_score(y_test, y_pred)
    logger = logging.getLogger(__name__)
    logger.info(
        f"Model has a coefficient R^2 of {score:.3f} on test data using a"
        " regressor of type '{type(regressor)}'"
    )
