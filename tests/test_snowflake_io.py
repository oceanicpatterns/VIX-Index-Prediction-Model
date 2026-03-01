import os
from unittest.mock import patch

import pytest

from vix_model.snowflake_io import get_connection_params, get_snowflake_connection


def test_get_connection_params_prefers_env(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_USER", "u")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "p")
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "a")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "w")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "d")
    monkeypatch.setenv("SNOWFLAKE_SCHEMA", "s")
    params = get_connection_params(config_path="config/does-not-exist.ini")
    assert params.user == "u"
    assert params.database == "d"


def test_get_connection_params_missing_values_raises(monkeypatch):
    for key in (
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    ):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValueError):
        get_connection_params(config_path="config/does-not-exist.ini")


def test_get_snowflake_connection_passes_connector_kwargs(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_USER", "u")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "p")
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "a")
    monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "w")
    monkeypatch.setenv("SNOWFLAKE_DATABASE", "d")
    monkeypatch.setenv("SNOWFLAKE_SCHEMA", "s")

    with patch("vix_model.snowflake_io.snowflake.connector.connect") as connect_mock:
        get_snowflake_connection(login_timeout=10)
    connect_mock.assert_called_once()
    assert connect_mock.call_args.kwargs["login_timeout"] == 10


@pytest.mark.skipif(
    os.getenv("RUN_SNOWFLAKE_INTEGRATION_TESTS") != "1",
    reason="Integration test disabled. Set RUN_SNOWFLAKE_INTEGRATION_TESTS=1 to enable.",
)
def test_snowflake_connection():
    conn = get_snowflake_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT CURRENT_VERSION()")
            version = cur.fetchone()[0]
        assert version
    finally:
        conn.close()
