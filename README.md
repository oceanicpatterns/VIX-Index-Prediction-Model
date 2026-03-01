# VIX-Index-Prediction-Model

Lightweight Python + data-engineering project for exploring VIX prediction with a simple baseline model and Snowflake-backed data flow.

Maintainer: **OceanicPatterns**  
Repository: https://github.com/oceanicpatterns/VIX-Index-Prediction-Model

## Table of Contents

- [Why This Project Exists](#why-this-project-exists)
- [Quick Navigation](#quick-navigation)
- [Background: VIX in Plain English](#background-vix-in-plain-english)
- [Architecture and Data Flow](#architecture-and-data-flow)
- [Interactive Demo Playground](#interactive-demo-playground)
- [Quick Start](#quick-start)
- [Configuration and Security](#configuration-and-security)
- [Run the Model](#run-the-model)
- [Run Tests](#run-tests)
- [CI and Quality Gates](#ci-and-quality-gates)
- [Project Structure](#project-structure)
- [Limitations and Next Steps](#limitations-and-next-steps)

## Why This Project Exists

This repository demonstrates a clean, testable workflow for:

1. Retrieving VIX historical data.
2. Building a derived volatility feature.
3. Persisting and reading modeled data through Snowflake.
4. Training and evaluating a baseline regression model.

It is designed as an educational baseline with production-minded engineering practices (typed contracts, tests, CI, secret hygiene).

## Quick Navigation

- App orchestration: [`src/vix_model/app.py`](src/vix_model/app.py)
- Core modeling logic: [`src/vix_model/modeling.py`](src/vix_model/modeling.py)
- Snowflake and config boundary: [`src/vix_model/snowflake_io.py`](src/vix_model/snowflake_io.py)
- Unit tests: [`tests/test_modeling.py`](tests/test_modeling.py), [`tests/test_snowflake_io.py`](tests/test_snowflake_io.py)
- Local static demo: [`docs/playground.html`](docs/playground.html)
- Demo entry for GitHub Pages: [`docs/index.html`](docs/index.html)
- CI workflows:
  - [`CI`](.github/workflows/ci.yml)
  - [`Deploy Demo (GitHub Pages)`](.github/workflows/pages.yml)

## Background: VIX in Plain English

The **VIX** (CBOE Volatility Index) is often called the market's "fear gauge."  
It reflects expected near-term volatility derived from S&P 500 options pricing.

In this project, the engineered feature is:

`VOLATILITY_INDEX = (HIGH - LOW) / CLOSE`

This is a simplified signal and not a complete market-volatility model. The goal here is to provide a transparent baseline pipeline, not trading advice.

## Architecture and Data Flow

### Workflow

1. Fetch CSV data from CBOE endpoint.
2. Validate expected input columns.
3. Compute `VOLATILITY_INDEX`.
4. Write/read data via Snowflake temp table.
5. Train/test split.
6. Fit linear regression.
7. Report MSE and sample prediction.

### Design Boundaries

- Domain modeling: [`modeling.py`](src/vix_model/modeling.py)
- Persistence + credentials: [`snowflake_io.py`](src/vix_model/snowflake_io.py)
- Runtime orchestration: [`app.py`](src/vix_model/app.py)
- Backward compatibility shims:
  - [`ml_vix_model.py`](ml_vix_model.py)
  - [`snowflake_connection.py`](snowflake_connection.py)

## Interactive Demo Playground

Use the static visitor demo to explore the project quickly:

- Live root URL: https://oceanicpatterns.github.io/VIX-Index-Prediction-Model/
- Live direct demo: https://oceanicpatterns.github.io/VIX-Index-Prediction-Model/playground.html
- Local file: [`docs/playground.html`](docs/playground.html)

Run locally:

```bash
open docs/playground.html
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python ml_vix_model.py
```

## Configuration and Security

Secrets are **not** committed to source control.

### Recommended (Environment Variables)

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
export VIX_PREDICTION_INPUT="0.40"
```

### Local Config Fallback

```bash
cp config/snowflake_config.example.ini config/snowflake_config.ini
```

Then fill local credentials in `config/snowflake_config.ini` (ignored by git).

## Run the Model

### Preferred (backward-compatible CLI style)

```bash
python ml_vix_model.py
```

### Installed console entrypoint

```bash
pip install .
run_vix_model
```

## Run Tests

### Unit tests (default)

```bash
pytest -q
```

### Snowflake integration test (opt-in)

```bash
RUN_SNOWFLAKE_INTEGRATION_TESTS=1 pytest -q
```

## CI and Quality Gates

On every push/PR:

1. Secret scan (`gitleaks`)
2. Python syntax check
3. Unit tests

Manual runs are enabled with `workflow_dispatch`.

## Project Structure

```text
VIX-Index-Prediction-Model/
  src/
    vix_model/
      __init__.py
      app.py
      modeling.py
      snowflake_io.py
  tests/
    test_modeling.py
    test_snowflake_io.py
  docs/
    index.html
    playground.html
  config/
    snowflake_config.example.ini
  ml_vix_model.py
  snowflake_connection.py
  pytest.ini
  requirements.txt
  setup.py
  LICENSE
```

## Limitations and Next Steps

- Current model is intentionally simple (single-feature linear regression).
- No feature store or experiment tracking yet.
- No advanced time-series modeling in current baseline.

Natural next extensions:

1. Add richer feature engineering (lags, rolling stats, macro signals).
2. Add model comparison (`LinearRegression`, tree models, regularized models).
3. Add data versioning and experiment logs.
4. Add model serving or batch prediction output contracts.

---

This repository is educational and not financial advice.
