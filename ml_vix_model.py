from __future__ import annotations

import os
import re
from dataclasses import dataclass
from io import StringIO
from typing import Mapping, Sequence

import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from snowflake_connection import get_snowflake_connection


VIX_DATA_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
DEFAULT_TABLE = "MASTER_DB.RAW.TEMP_TABLE"
TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*){2}$")


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


def _validate_table_name(table_name: str) -> str:
    if not TABLE_NAME_PATTERN.match(table_name):
        raise ValueError(
            "Invalid table name format. Expected fully-qualified DB.SCHEMA.TABLE with "
            "letters, numbers, and underscores only."
        )
    return table_name


def create_temp_table(conn: object, table_name: str) -> None:
    table = _validate_table_name(table_name)
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {table} "
            "(DATE DATE, CLOSE_PRICE NUMBER, VOLATILITY_INDEX FLOAT)"
        )


def insert_data_to_temp_table(conn: object, df: pd.DataFrame, table_name: str) -> None:
    table = _validate_table_name(table_name)
    with conn.cursor() as cur:
        payload = df.copy()
        payload["DATE"] = payload["DATE"].dt.strftime("%Y-%m-%d")
        rows = [tuple(row) for row in payload[["DATE", "CLOSE", "VOLATILITY_INDEX"]].values]
        cur.executemany(f"INSERT INTO {table} VALUES (%s, %s, %s)", rows)


def fetch_data_from_temp_table(conn: object, table_name: str) -> pd.DataFrame:
    table = _validate_table_name(table_name)
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["DATE", "CLOSE_PRICE", "VOLATILITY_INDEX"])


def _fit_and_evaluate(
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


def _build_report(result: TrainingResult) -> str:
    return (
        "Our model predicts VIX CLOSE_PRICE from VOLATILITY_INDEX. "
        f"MSE on unseen data: {result.mse:.4f}. "
        f"Train rows: {result.train_rows}, Test rows: {result.test_rows}. "
        f"Sample prediction @ VOLATILITY_INDEX=0.40: {result.predicted_close_for_input:.2f}."
    )


def run_training_and_generate_results() -> Mapping[str, float | int]:
    table_name = os.getenv("SNOWFLAKE_TEMP_TABLE", DEFAULT_TABLE)
    prediction_input = float(os.getenv("VIX_PREDICTION_INPUT", "0.40"))
    conn = get_snowflake_connection()
    try:
        data_processor = DataProcessor(VIX_DATA_URL)
        df = data_processor.fetch_data_from_url()
        df = data_processor.calculate_volatility_index(df)

        create_temp_table(conn, table_name=table_name)
        insert_data_to_temp_table(conn, df, table_name=table_name)
        fetched_df = fetch_data_from_temp_table(conn, table_name=table_name)

        result = _fit_and_evaluate(
            features=fetched_df[["VOLATILITY_INDEX"]],
            targets=fetched_df["CLOSE_PRICE"],
            predict_for=prediction_input,
        )
        print(_build_report(result))
        return result.to_dict()
    finally:
        conn.close()


if __name__ == "__main__":
    run_training_and_generate_results()
