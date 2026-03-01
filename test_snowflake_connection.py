import os

import pytest

from snowflake_connection import get_snowflake_connection


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
