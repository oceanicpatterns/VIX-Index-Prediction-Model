import configparser
import os
from pathlib import Path
from typing import Dict

import snowflake.connector


REQUIRED_FIELDS = ("user", "password", "account", "warehouse", "database", "schema")


def _load_from_config(config_path: Path) -> Dict[str, str]:
    parser = configparser.ConfigParser()
    if not config_path.exists():
        return {}
    parser.read(config_path)
    if "snowflake" not in parser:
        return {}
    return {key: parser["snowflake"].get(key, "") for key in REQUIRED_FIELDS}


def _load_from_env() -> Dict[str, str]:
    return {
        "user": os.getenv("SNOWFLAKE_USER", ""),
        "password": os.getenv("SNOWFLAKE_PASSWORD", ""),
        "account": os.getenv("SNOWFLAKE_ACCOUNT", ""),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", ""),
        "database": os.getenv("SNOWFLAKE_DATABASE", ""),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", ""),
    }


def get_connection_params(config_path: str | None = None) -> Dict[str, str]:
    config_file = Path(
        config_path or os.getenv("SNOWFLAKE_CONFIG_PATH", "config/snowflake_config.ini")
    )
    values = _load_from_config(config_file)
    env_values = _load_from_env()

    # Environment variables always take precedence over file values.
    merged = {field: env_values[field] or values.get(field, "") for field in REQUIRED_FIELDS}
    missing = [field for field, value in merged.items() if not value]

    if missing:
        missing_csv = ", ".join(missing)
        raise ValueError(
            "Missing Snowflake settings: "
            f"{missing_csv}. Set SNOWFLAKE_* environment variables or provide "
            f"values in {config_file}."
        )

    return merged


def get_snowflake_connection(config_path: str | None = None):
    params = get_connection_params(config_path=config_path)
    return snowflake.connector.connect(
        user=params["user"],
        password=params["password"],
        account=params["account"],
        warehouse=params["warehouse"],
        database=params["database"],
        schema=params["schema"],
    )
