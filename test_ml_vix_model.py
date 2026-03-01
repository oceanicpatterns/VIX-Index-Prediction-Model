from unittest.mock import Mock, patch

import pandas as pd
import pytest

from ml_vix_model import DataProcessor, _fit_and_evaluate, _validate_table_name


def test_fetch_data_from_url_parses_required_columns():
    csv_body = "DATE,OPEN,HIGH,LOW,CLOSE\n2024-01-01,10,12,9,11\n"
    fake_response = Mock()
    fake_response.text = csv_body
    fake_response.raise_for_status = Mock()

    with patch("ml_vix_model.requests.get", return_value=fake_response) as mock_get:
        df = DataProcessor("https://example.com/vix.csv").fetch_data_from_url(timeout=5)

    mock_get.assert_called_once_with("https://example.com/vix.csv", timeout=5)
    assert list(df.columns) == ["DATE", "OPEN", "HIGH", "LOW", "CLOSE"]
    assert len(df) == 1


def test_calculate_volatility_index_returns_expected_columns():
    input_df = pd.DataFrame(
        {
            "DATE": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "HIGH": [20.0, 22.0],
            "LOW": [10.0, 11.0],
            "CLOSE": [15.0, 16.0],
        }
    )

    output_df = DataProcessor("https://example.com").calculate_volatility_index(input_df)
    assert list(output_df.columns) == ["DATE", "CLOSE", "VOLATILITY_INDEX"]
    assert output_df["VOLATILITY_INDEX"].iloc[0] == pytest.approx((20.0 - 10.0) / 15.0)


def test_validate_table_name_accepts_fully_qualified_name():
    assert _validate_table_name("MASTER_DB.RAW.TEMP_TABLE") == "MASTER_DB.RAW.TEMP_TABLE"


def test_validate_table_name_rejects_invalid_name():
    with pytest.raises(ValueError):
        _validate_table_name("raw.temp_table")


def test_fit_and_evaluate_returns_expected_shape():
    features = pd.DataFrame({"VOLATILITY_INDEX": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]})
    targets = pd.Series([20, 25, 30, 35, 40, 45], name="CLOSE_PRICE")
    result = _fit_and_evaluate(features=features, targets=targets, predict_for=0.4)
    assert result.train_rows > 0
    assert result.test_rows > 0
    assert result.mse >= 0
    assert isinstance(result.predicted_close_for_input, float)


def test_fit_and_evaluate_raises_for_empty_data():
    with pytest.raises(ValueError):
        _fit_and_evaluate(
            features=pd.DataFrame({"VOLATILITY_INDEX": []}),
            targets=pd.Series([], dtype=float, name="CLOSE_PRICE"),
            predict_for=0.4,
        )
