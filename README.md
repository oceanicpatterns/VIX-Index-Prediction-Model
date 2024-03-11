# VIX-Index-Prediction-Model

Demonstrates a workflow that involves fetching, processing, storing, analyzing, and reporting on financial data using machine learning techniques within a Snowflake database environment

## Overview

The VIX Index, also known as the CBOE Volatility Index, is a real-time market index that reflects the market's expectations for volatility over the next 30 days. It measures the relative strength of market sentiment and fear among participants by analyzing the prices of S&P 500 index options with near-term expiration dates. Essentially, the VIX provides a quantifiable measure of market risk and helps investors gauge the level of risk or stress in the market when making investment decisions.

Accurate prediction of the VIX can be valuable for risk management. This script aims to provide a simple way to predict the VIX 'CLOSE PRICE' using historical data.

## Data Source

The data used in this project is sourced from the CBOE VIX Historical Data website, which provides historical price data for the VIX Index, VIX futures, and other volatility indices. Users can access daily closing values of the Cboe Volatility Index® (VIX Index) and other related indices.

## Features

- Fetches historical VIX Index data from a specified URL.
- Calculates the 'VOLATILITY INDEX' from the high, low, and close prices.
- Interacts with Snowflake to create a temporary table, insert data, and fetch it for model training.
- Trains a Linear Regression model using the 'VOLATILITY INDEX' as a feature.
- Evaluates the model's performance using the Mean Squared Error (MSE) metric.
- Generates a brief report detailing the model's prediction accuracy.

## Requirements

- Python 3.7 or later (strongly recommended, as 3.6 is nearing end-of-life)
- Some familiarity with Snowflake concepts (understanding of tables, columns, and data manipulation)

## Installation and Setup

### 1. Configure Snowflake Account:

Go to snowflake > config > snowflake_config.ini and fill in the required fields for your Snowflake account.
To use Snowflake, you can sign up for a free trial here.

To use snowflake, you need to create a free trial here: https://signup.snowflake.com

### 2. Create a Virtual Environment:
Navigate to the project directory and create a virtual environment named 'vix-env' using the following commands:

```bash
# For Unix/MacOS
python3 -m venv vix-env

# For Windows
python -m venv vix-env
```

Activate the virtual environment before installing dependencies:
```bash
# For Unix/MacOS
source vix-env/bin/activate

# For Windows
.\vix-env\Scripts\activate
```

Once the virtual environment is activated, install the project dependencies using setup.py:
```bash
pip install .
```

This command will read the dependencies specified in setup.py and install them in your virtual environment.

You can now run the VIX Index Prediction Model by executing the main script:

```bash
python ml_vix_model.py
```

## Disclaimer
This code is provided for educational and learning purposes only. It is not intended to be a product for sale, distribution, or to make a profit. The implementation serves as a basic example of data science and machine learning concepts and should not be used as a financial advisory tool.

The CBOE Volatility Index data is compiled for the convenience of site visitors and is provided without responsibility for accuracy. Users accept this data on the condition that transmission or omissions shall not be the basis for any claim, demand, or cause for action. For more information on the data sources and terms of use, please visit [CBOE VIX Historical Data](https://www.cboe.com/tradable_products/vix/vix_historical_data/).