import os
import re
from io import StringIO

import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from snowflake_connection import get_snowflake_connection


VIX_DATA_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
DEFAULT_TABLE = "MASTER_DB.RAW.TEMP_TABLE"
TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*){2}$")


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


def create_temp_table(conn, table_name: str) -> None:
    table = _validate_table_name(table_name)
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {table} "
            "(DATE DATE, CLOSE_PRICE NUMBER, VOLATILITY_INDEX FLOAT)"
        )


def insert_data_to_temp_table(conn, df: pd.DataFrame, table_name: str) -> None:
    table = _validate_table_name(table_name)
    with conn.cursor() as cur:
        payload = df.copy()
        payload["DATE"] = payload["DATE"].dt.strftime("%Y-%m-%d")
        rows = [tuple(row) for row in payload[["DATE", "CLOSE", "VOLATILITY_INDEX"]].values]
        cur.executemany(f"INSERT INTO {table} VALUES (%s, %s, %s)", rows)


def fetch_data_from_temp_table(conn, table_name: str) -> pd.DataFrame:
    table = _validate_table_name(table_name)
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["DATE", "CLOSE_PRICE", "VOLATILITY_INDEX"])


def run_training_and_generate_results() -> dict:
    table_name = os.getenv("SNOWFLAKE_TEMP_TABLE", DEFAULT_TABLE)
    conn = get_snowflake_connection()
    try:
        data_processor = DataProcessor(VIX_DATA_URL)
        df = data_processor.fetch_data_from_url()
        df = data_processor.calculate_volatility_index(df)

        create_temp_table(conn, table_name=table_name)
        insert_data_to_temp_table(conn, df, table_name=table_name)
        fetched_df = fetch_data_from_temp_table(conn, table_name=table_name)

        X, y = fetched_df[["VOLATILITY_INDEX"]], fetched_df["CLOSE_PRICE"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = LinearRegression()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)

        report = (
            "Our model predicts VIX CLOSE_PRICE from VOLATILITY_INDEX. "
            f"The Mean Squared Error (MSE) on unseen test data is {mse:.4f}."
        )
        print(report)
        return {"mse": float(mse), "train_rows": int(len(X_train)), "test_rows": int(len(X_test))}
    finally:
        conn.close()


if __name__ == "__main__":
    run_training_and_generate_results()
