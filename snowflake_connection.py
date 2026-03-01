"""Backward-compatible Snowflake connection shim.

Runtime implementation now lives in `src/vix_model/`.
"""

from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from vix_model.snowflake_io import SnowflakeSettings, get_connection_params, get_snowflake_connection

__all__ = ["SnowflakeSettings", "get_connection_params", "get_snowflake_connection"]
