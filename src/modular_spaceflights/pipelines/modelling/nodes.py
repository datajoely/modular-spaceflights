import logging
from typing import Any, Dict, Tuple, Union

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split


def split_data(data: pd.DataFrame, split_options: Dict) -> Tuple:
    """Splits data into features and targets training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters.yml.
    Returns:
        Split data.
    """
    target_variable = split_options["target"]
    independent_variables = set(target_variable) - set(data.columns)
    test_size = split_options["test_size"]
    random_state = split_options["random_state"]

    logger = logging.getLogger(__name__)
    logger.info(
        f"Splitting data for the following independent variables "
        f"{independent_variables} against the target of '{target_variable}' "
        f"with a test sized of {test_size} and a random state of "
        f"'{random_state}'"
    )

    X = data[independent_variables]
    y = data[target_variable]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test


def train_model(
    X_train: pd.DataFrame, y_train: pd.Series, model_options: Dict[str, Any]
) -> Tuple[Union[LinearRegression, RandomForestRegressor], Dict[str, Any]]:
    """Trains the linear regression model.

    Args:
        X_train: Training data of independent features.
        y_train: Training data for price.

    Returns:
        Trained model.
    """

    model_type = model_options.get("class")
    model_arguments = model_options.get("kwargs")

    # This could be even more generic, but in this case we are able to be specific
    acceptable_model_types = ["LinearRegression", "RandomForestRegressor"]
    if model_type == acceptable_model_types[0]:
        regressor_class = LinearRegression
    elif model_type == acceptable_model_types[1]:
        regressor_class = RandomForestRegressor
    else:
        raise ValueError(
            f"Please provide one of {acceptable_model_types} "
            f"as acceptable arguments"
        )

    regressor_instance = regressor_class(**model_arguments)
    logger = logging.getLogger(__name__)
    logger.info(f"Fitting model of type {type(regressor_instance)}")

    regressor_instance.fit(X_train, y_train)
    flat_model_params = {**{"model_type": model_type}, **model_arguments}
    return regressor_instance, flat_model_params


def evaluate_model(
    regressor: Union[LinearRegression, RandomForestRegressor],
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Dict[str, float]:
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
        f"Model has a coefficient R^2 of {score:.3f} on test data using a "
        f"regressor of type '{type(regressor)}'"
    )
    return {"r2_score": score}
