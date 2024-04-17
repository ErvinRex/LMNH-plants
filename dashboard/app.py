"""
Python script for visualising and hosting a dashboard for LMNH plant data
"""

from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from boto3 import client
from pymssql import connect


def get_db_connection(config: dict) -> connect:
    """Returns database connection."""

    return connect(
        server=config["DB_HOST"],
        port=config["DB_PORT"],
        user=config["DB_USER"],
        database=config["DB_NAME"],
        password=config["DB_PASSWORD"],
        as_dict=True
    )


# def get_merged_data(conn) -> pd.DataFrame:
#     """Access redshift database to get merged data"""
#     curr = get_cursor(conn)
#     sql_query = """SELECT *
#                     FROM s_beta.recording AS r
#                     JOIN s_beta.plant AS p
#                         ON r.plant_id = p.plant_id
#                     JOIN s_beta.origin AS o
#                         ON p.origin_id = o.origin_id
#                     JOIN s_beta.botanist AS b
#                         ON r.botanist_id = b.botanist_id
#                     JOIN s_beta.image as i
#                         ON r.image_id = i.image_id
#                     ;
#                     """
#     curr.execute(sql_query)
#     rows = curr.fetchall()
#     data = pd.DataFrame(rows)
#     return data

def get_filter_variables() -> int:
    """Get the filter variables for filtering charts from streamlit multi-select"""

    with conn.cursor() as curr:
        sql_query = """
                    SELECT p.plant_id
                    FROM s_beta.plant AS p
                    """
        
        curr.execute(sql_query)
        rows = curr.fetchall()
        plant_ids = [plant_id.get('plant_id') for plant_id in rows]
        plant_id_selected = st.sidebar.selectbox("Plant Selection:",
                                            plant_ids)

    return plant_id_selected

def get_plant_details(conn, plant_id_selected: int):
    """Get the relevant plant_id details to be displayed"""
    with conn.cursor() as curr:
        sql_query = """
                    SELECT p.plant_id, p.plant_name, p.scientific_name, o.place_name, o.country_code, o.timezone
                    FROM s_beta.plant AS p
                    LEFT JOIN s_beta.origin AS o
                        ON p.origin_id = o.origin_id
                    WHERE p.plant_id = %d
                    ;
                    """

        curr.execute(sql_query, plant_id_selected)
        row = curr.fetchone()

    plant_name = row.get('plant_name')
    scientific_name = row.get('scientific_name')
    origin = f"{row.get('country_code')}, {row.get('place_name')}, {row.get('timezone')}"
    return plant_name, scientific_name, origin

if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    st.sidebar.title(":rainbow[LMNH Plant Recordings Dashboard]")
    st.sidebar.subheader("Plant recordings, no better way to see 'em")

    plant_id_selected = get_filter_variables()
    st.sidebar.subheader("Plant Summary", divider="rainbow")

    plant_name, scientific_name, origin = get_plant_details(conn, plant_id_selected)

    st.sidebar.write(f"Plant Name: {plant_name}")
    st.sidebar.write(f"Scientific Name: {scientific_name}")
    st.sidebar.write(f"Country, Location, Timezone: {origin}")

    conn.close()