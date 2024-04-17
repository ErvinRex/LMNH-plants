import asyncio

from dotenv import load_dotenv
from extract import fetch_data_from_endpoints
from transform import transform
from load import upload_data
from os import environ as ENV
from pymssql import connect

load_dotenv()

# Config for uploading to AWS RDS
DB_HOST = ENV["DB_HOST"]
DB_NAME = ENV["DB_NAME"]
DB_USER = ENV["DB_USER"]
DB_PORT = ENV["DB_PORT"]
DB_PASSWORD = ENV["DB_PASSWORD"]


async def main():
    conn = connect(
        server=ENV["DB_HOST"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        port=ENV["DB_PORT"],
        as_dict=True,
    )

    urls = [f"https://data-eng-plants-api.herokuapp.com/plants/{i}" for i in range(51)]

    extract_data = await fetch_data_from_endpoints(urls)

    transform_data = transform(extract_data)

    upload_data(transform_data, conn)


def handler(event, context):
    asyncio.run(main())
