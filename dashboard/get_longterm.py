
from os import environ as ENV

from dotenv import load_dotenv
from pymssql import connect

def get_db_connection(config):
    """Returns a live database connection."""

    return connect(
        server=config["DB_HOST"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        database=config["DB_NAME"],
        port=config["DB_PORT"],
        as_dict=True
    )

if __name__ == '__main__':
    config = load_dotenv()
    get_db_connection(ENV)