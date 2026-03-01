"""Backward-compatible entrypoint shim.

Runtime implementation now lives in `src/vix_model/`.
"""

from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from vix_model.app import run_training_and_generate_results
from vix_model.modeling import DataProcessor, TrainingResult, build_report, fit_and_evaluate
from vix_model.snowflake_io import (
    DEFAULT_TABLE,
    create_temp_table,
    fetch_data_from_temp_table,
    insert_data_to_temp_table,
    validate_table_name,
)

__all__ = [
    "DEFAULT_TABLE",
    "DataProcessor",
    "TrainingResult",
    "build_report",
    "create_temp_table",
    "fetch_data_from_temp_table",
    "fit_and_evaluate",
    "insert_data_to_temp_table",
    "run_training_and_generate_results",
    "validate_table_name",
]


if __name__ == "__main__":
    run_training_and_generate_results()
