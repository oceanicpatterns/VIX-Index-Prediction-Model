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

## Interactive Demo Playground

Explore the static browser demo:

- Local file: `docs/playground.html`
- Direct GitHub URL: `https://github.com/oceanicpatterns/VIX-Index-Prediction-Model/blob/main/docs/playground.html`
- Live Pages URL (after enabling Pages): `https://oceanicpatterns.github.io/VIX-Index-Prediction-Model/`

Run locally:

```bash
open docs/playground.html
```

Enable GitHub Pages for live visitors:

1. Repository Settings -> Pages
2. Source: GitHub Actions
3. Run workflow `Deploy Demo (GitHub Pages)` once (or push to `main`)

What visitors can do in the playground:

1. Simulate VIX-like volatility/close-price data.
2. Tune sample size and noise.
3. Re-run a baseline linear model instantly.
4. Inspect train/test split, MSE, prediction output, and chart behavior.

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

Or via installed console script:

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
  src/vix_model/
    app.py
    modeling.py
    snowflake_io.py
    __init__.py
  tests/
    test_modeling.py
    test_snowflake_io.py
  docs/
    playground.html
  config/
    snowflake_config.example.ini
  ml_vix_model.py              # backward-compatible shim
  snowflake_connection.py      # backward-compatible shim
  pytest.ini
  requirements.txt
  setup.py
```

## Notes

- This is an educational baseline model, not financial advice.
- The model is intentionally simple and should be extended before production use.
