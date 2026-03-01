from __future__ import annotations

import os
from typing import Mapping

from .modeling import DataProcessor, VIX_DATA_URL, build_report, fit_and_evaluate
from .snowflake_io import (
    DEFAULT_TABLE,
    create_temp_table,
    fetch_data_from_temp_table,
    get_snowflake_connection,
    insert_data_to_temp_table,
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

        result = fit_and_evaluate(
            features=fetched_df[["VOLATILITY_INDEX"]],
            targets=fetched_df["CLOSE_PRICE"],
            predict_for=prediction_input,
        )
        print(build_report(result))
        return result.to_dict()
    finally:
        conn.close()
