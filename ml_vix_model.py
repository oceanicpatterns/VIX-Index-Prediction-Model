import pandas as pd
import requests
from io import StringIO
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from snowflake_connection import get_snowflake_connection

class DataProcessor:
    def __init__(self, url):
        self.url = url

    def fetch_data_from_url(self):
        response = requests.get(self.url)
        data = response.content.decode('utf-8')
        return pd.read_csv(StringIO(data), parse_dates=['DATE'])

    def calculate_volatility_index(self, df):
        df['VOLATILITY_INDEX'] = (df['HIGH'] - df['LOW']) / df['CLOSE']
        return df[['DATE', 'CLOSE', 'VOLATILITY_INDEX']]

# Change the name of your Database, Schema and Table
def create_temp_table(conn):
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS MASTER_DB.RAW.TEMP_TABLE")
        cur.execute("CREATE TABLE IF NOT EXISTS MASTER_DB.RAW.TEMP_TABLE (DATE DATE, CLOSE_PRICE NUMBER, VOLATILITY_INDEX FLOAT)")

def insert_data_to_temp_table(conn, df):
    with conn.cursor() as cur:
        df['DATE'] = df['DATE'].dt.strftime('%Y-%m-%d')

        # Prepare the data for insertion as a list of tuples
        data_to_insert = [tuple(row) for row in df[['DATE', 'CLOSE', 'VOLATILITY_INDEX']].values]

        # Execute the bulk insert operation
        # Executemany() method provided by the Snowflake connector allows to insert multiple rows in a single operation
        cur.executemany("INSERT INTO MASTER_DB.RAW.TEMP_TABLE VALUES (%s, %s, %s)", data_to_insert)

def fetch_data_from_temp_table(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM MASTER_DB.RAW.TEMP_TABLE")
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=['DATE', 'CLOSE_PRICE', 'VOLATILITY_INDEX'])

def run_training_and_generate_results():
    url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
    conn = get_snowflake_connection()

    data_processor = DataProcessor(url)
    df = data_processor.fetch_data_from_url()
    df = data_processor.calculate_volatility_index(df)

    create_temp_table(conn)
    insert_data_to_temp_table(conn, df)

    fetched_df = fetch_data_from_temp_table(conn)

    X, y = fetched_df[['VOLATILITY_INDEX']], fetched_df['CLOSE_PRICE']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)

    report = "Our model has been trained to predict the 'CLOSE PRICE' of VIX Index based on its 'VOLATILITY INDEX'. " \
         "After testing the model on unseen data, we found that its predictions were on average {:.2f} units away from the actual prices. " \
         "This means if our model predicts a 'CLOSE PRICE' of 100 units, you can expect the actual price to be between {:.2f} and {:.2f} units.".format(mse, 100-mse, 100+mse)


    print(report)

if __name__ == "__main__":
    run_training_and_generate_results()