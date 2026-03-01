from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from typing import Mapping

import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


VIX_DATA_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"


@dataclass(frozen=True)
class TrainingResult:
    mse: float
    train_rows: int
    test_rows: int
    predicted_close_for_input: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "mse": self.mse,
            "train_rows": self.train_rows,
            "test_rows": self.test_rows,
            "predicted_close_for_input": self.predicted_close_for_input,
        }


class DataProcessor:
    def __init__(self, url: str):
        self.url = url

    def fetch_data_from_url(self, timeout: int = 30) -> pd.DataFrame:
        response = requests.get(self.url, timeout=timeout)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), parse_dates=["DATE"])
        required = {"DATE", "HIGH", "LOW", "CLOSE"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Required columns missing from source data: {sorted(missing)}")
        return df

    def calculate_volatility_index(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["VOLATILITY_INDEX"] = (out["HIGH"] - out["LOW"]) / out["CLOSE"]
        out = out.replace([float("inf"), float("-inf")], pd.NA)
        out = out.dropna(subset=["DATE", "CLOSE", "VOLATILITY_INDEX"])
        return out[["DATE", "CLOSE", "VOLATILITY_INDEX"]]


def fit_and_evaluate(
    features: pd.DataFrame, targets: pd.Series, predict_for: float
) -> TrainingResult:
    if features.empty or targets.empty:
        raise ValueError("Training data is empty. Cannot fit model.")

    X_train, X_test, y_train, y_test = train_test_split(
        features, targets, test_size=0.2, random_state=42
    )
    if X_train.empty or X_test.empty:
        raise ValueError("Insufficient rows after train-test split.")

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    single_prediction = float(model.predict(pd.DataFrame({"VOLATILITY_INDEX": [predict_for]}))[0])

    return TrainingResult(
        mse=float(mse),
        train_rows=int(len(X_train)),
        test_rows=int(len(X_test)),
        predicted_close_for_input=single_prediction,
    )


def build_report(result: TrainingResult) -> str:
    return (
        "Our model predicts VIX CLOSE_PRICE from VOLATILITY_INDEX. "
        f"MSE on unseen data: {result.mse:.4f}. "
        f"Train rows: {result.train_rows}, Test rows: {result.test_rows}. "
        f"Sample prediction @ VOLATILITY_INDEX=0.40: {result.predicted_close_for_input:.2f}."
    )
