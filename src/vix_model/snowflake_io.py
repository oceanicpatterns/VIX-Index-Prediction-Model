from __future__ import annotations

import configparser
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping

import pandas as pd
import snowflake.connector
from snowflake.connector.connection import SnowflakeConnection


REQUIRED_FIELDS = ("user", "password", "account", "warehouse", "database", "schema")
DEFAULT_TABLE = "MASTER_DB.RAW.TEMP_TABLE"
TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*){2}$")


@dataclass(frozen=True)
class SnowflakeSettings:
    user: str
    password: str
    account: str
    warehouse: str
    database: str
    schema: str

    def to_connect_kwargs(self) -> Dict[str, str]:
        return {
            "user": self.user,
            "password": self.password,
            "account": self.account,
            "warehouse": self.warehouse,
            "database": self.database,
            "schema": self.schema,
        }


def load_settings_from_config(config_path: Path) -> Mapping[str, str]:
    parser = configparser.ConfigParser()
    if not config_path.exists():
        return {}
    parser.read(config_path)
    if "snowflake" not in parser:
        return {}
    return {key: parser["snowflake"].get(key, "") for key in REQUIRED_FIELDS}


def load_settings_from_env() -> Mapping[str, str]:
    return {
        "user": os.getenv("SNOWFLAKE_USER", ""),
        "password": os.getenv("SNOWFLAKE_PASSWORD", ""),
        "account": os.getenv("SNOWFLAKE_ACCOUNT", ""),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", ""),
        "database": os.getenv("SNOWFLAKE_DATABASE", ""),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", ""),
    }


def get_connection_params(config_path: str | None = None) -> SnowflakeSettings:
    config_file = Path(
        config_path or os.getenv("SNOWFLAKE_CONFIG_PATH", "config/snowflake_config.ini")
    )
    values = load_settings_from_config(config_file)
    env_values = load_settings_from_env()

    merged = {field: env_values[field] or values.get(field, "") for field in REQUIRED_FIELDS}
    missing = [field for field, value in merged.items() if not value]
    if missing:
        missing_csv = ", ".join(missing)
        raise ValueError(
            "Missing Snowflake settings: "
            f"{missing_csv}. Set SNOWFLAKE_* environment variables or provide "
            f"values in {config_file}."
        )

    return SnowflakeSettings(**merged)


def get_snowflake_connection(
    config_path: str | None = None, **connector_kwargs: Any
) -> SnowflakeConnection:
    params = get_connection_params(config_path=config_path)
    return snowflake.connector.connect(**params.to_connect_kwargs(), **connector_kwargs)


def validate_table_name(table_name: str) -> str:
    if not TABLE_NAME_PATTERN.match(table_name):
        raise ValueError(
            "Invalid table name format. Expected fully-qualified DB.SCHEMA.TABLE with "
            "letters, numbers, and underscores only."
        )
    return table_name


def create_temp_table(conn: SnowflakeConnection, table_name: str) -> None:
    table = validate_table_name(table_name)
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {table} "
            "(DATE DATE, CLOSE_PRICE NUMBER, VOLATILITY_INDEX FLOAT)"
        )


def insert_data_to_temp_table(
    conn: SnowflakeConnection, df: pd.DataFrame, table_name: str
) -> None:
    table = validate_table_name(table_name)
    with conn.cursor() as cur:
        payload = df.copy()
        payload["DATE"] = payload["DATE"].dt.strftime("%Y-%m-%d")
        rows = [tuple(row) for row in payload[["DATE", "CLOSE", "VOLATILITY_INDEX"]].values]
        cur.executemany(f"INSERT INTO {table} VALUES (%s, %s, %s)", rows)


def fetch_data_from_temp_table(conn: SnowflakeConnection, table_name: str) -> pd.DataFrame:
    table = validate_table_name(table_name)
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["DATE", "CLOSE_PRICE", "VOLATILITY_INDEX"])
