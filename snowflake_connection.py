import configparser
import snowflake.connector

def get_snowflake_connection():
    config = configparser.ConfigParser()
    config.read('config/snowflake_config.ini')

    return snowflake.connector.connect(
        user=config['snowflake']['user'],
        password=config['snowflake']['password'],
        account=config['snowflake']['account'],
        warehouse=config['snowflake']['warehouse'],
        database=config['snowflake']['database'],
        schema=config['snowflake']['schema']
    )