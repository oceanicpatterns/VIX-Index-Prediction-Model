import unittest
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from snowflake_connection import get_snowflake_connection
from ml_vix_model import DataProcessor, create_temp_table, insert_data_to_temp_table, fetch_data_from_temp_table

class TestDataProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
        cls.conn = get_snowflake_connection()
        cls.data_processor = DataProcessor(cls.url)
        cls.df = cls.data_processor.fetch_data_from_url()
        cls.df = cls.data_processor.calculate_volatility_index(cls.df)

    def test_data_processing(self):
        self.assertIsNotNone(self.df)
        self.assertIsInstance(self.df, pd.DataFrame)
        self.assertTrue('DATE' in self.df.columns)
        self.assertTrue('VOLATILITY_INDEX' in self.df.columns)

    def test_snowflake_operations(self):
        create_temp_table(self.conn)
        insert_data_to_temp_table(self.conn, self.df)
        fetched_df = fetch_data_from_temp_table(self.conn)

        self.assertIsNotNone(fetched_df)
        self.assertIsInstance(fetched_df, pd.DataFrame)


    def test_model_training_and_evaluation(self):
        X, y = self.df[['VOLATILITY_INDEX']], self.df['CLOSE']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)

        self.assertIsInstance(model, LinearRegression)
        self.assertTrue(mse >= 0)  # Ensure MSE is non-negative

if __name__ == '__main__':
    unittest.main()