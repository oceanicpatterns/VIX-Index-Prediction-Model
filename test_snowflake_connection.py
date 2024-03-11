
import snowflake.connector
from snowflake_connection import get_snowflake_connection

def test_snowflake_connection():
    
    try:
        conn = get_snowflake_connection()
        cur = conn.cursor()
        print("Successfully connected to Snowflake.")
        
        try:
            cur.execute("SELECT CURRENT_VERSION()")
            one_row = cur.fetchone()
            print(f"Snowflake version: {one_row[0]}")
        except snowflake.connector.errors.ProgrammingError as e:
            print(f"An error occurred during query execution: {e}")
        finally:
            cur.close()

    except Exception as e:
        print(f"Failed to connect to Snowflake: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_snowflake_connection()