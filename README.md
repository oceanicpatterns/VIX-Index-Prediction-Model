# VIX-Index-Prediction-Model

Lightweight VIX modeling project that fetches historical CBOE VIX data, engineers a simple volatility feature, stores data in Snowflake, and trains a baseline linear regression model.

## Maintainer

- Maintainer: **OceanicPatterns**
- Repository: `https://github.com/oceanicpatterns/VIX-Index-Prediction-Model`

## What This Project Does

1. Downloads VIX historical data from CBOE.
2. Computes `VOLATILITY_INDEX = (HIGH - LOW) / CLOSE`.
3. Writes/reads a Snowflake table for model-ready data.
4. Trains and evaluates a baseline model using Mean Squared Error (MSE).

## Security and Configuration

Credentials are **not** stored in source control.

Use either:

1. Environment variables (recommended)
2. Local config file `config/snowflake_config.ini` (ignored by git)

### Environment Variables

```bash
export SNOWFLAKE_USER="..."
export SNOWFLAKE_PASSWORD="..."
export SNOWFLAKE_ACCOUNT="..."
export SNOWFLAKE_WAREHOUSE="..."
export SNOWFLAKE_DATABASE="..."
export SNOWFLAKE_SCHEMA="..."
```

Optional:

```bash
export SNOWFLAKE_TEMP_TABLE="MASTER_DB.RAW.TEMP_TABLE"
```

### Config File Option (Local Only)

Copy the template:

```bash
cp config/snowflake_config.example.ini config/snowflake_config.ini
```

Then fill in your local credentials.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python ml_vix_model.py
```

Or via console script:

```bash
pip install .
run_vix_model
```

## Tests

Unit tests (default):

```bash
pytest -q
```

Snowflake integration test is disabled by default. Enable it explicitly:

```bash
RUN_SNOWFLAKE_INTEGRATION_TESTS=1 pytest -q
```

## CI

GitHub Actions runs on push/PR:

1. Secret scan (`gitleaks`)
2. Python syntax check
3. Unit tests

## Project Layout

```text
VIX-Index-Prediction-Model/
  config/
    snowflake_config.example.ini
  ml_vix_model.py
  snowflake_connection.py
  test_ml_vix_model.py
  test_snowflake_connection.py
  requirements.txt
  setup.py
```

## Notes

- This is an educational baseline model, not financial advice.
- The model is intentionally simple and should be extended before production use.
