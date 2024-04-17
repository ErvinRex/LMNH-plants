"""
Python script for visualising and hosting a dashboard for LMNH plant data
"""

from os import environ as ENV
from datetime import datetime, timezone, timedelta
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


def get_filter_variables(conn: connect) -> int:
    """Get the filter variables for filtering charts from streamlit multi-select"""

    with conn.cursor() as curr:
        query = "SELECT plant_id, plant_name FROM s_beta.plant"
        curr.execute(query, )
        rows = curr.fetchall()
    plant_ids = [plant_id.get('plant_id') for plant_id in rows]
    plant_id_selected = st.sidebar.selectbox("Plant Selection:", plant_ids)

    return plant_id_selected


def get_plant_details(conn: connect, plant_id_selected: int) -> tuple:
    """Get the relevant plant_id details to be displayed"""

    with conn.cursor() as curr:
        query = """
                SELECT p.plant_id, p.plant_name, p.scientific_name, o.place_name, o.country_code, o.timezone
                FROM s_beta.plant AS p
                LEFT JOIN s_beta.origin AS o
                    ON p.origin_id = o.origin_id
                WHERE p.plant_id = %d
                """

        curr.execute(query, plant_id_selected)
        row = curr.fetchone()

    plant_name = row.get('plant_name')
    scientific_name = row.get('scientific_name')
    origin = f"{row.get('country_code', "(country_code)")}, {row.get('place_name', "(place_name)")}, {
        row.get('timezone', "(timezone)")}"

    return plant_name, scientific_name, origin


def get_total_plant_count(conn: connect) -> int:
    """Returns total plant count."""

    query = "SELECT COUNT(plant_id) AS count FROM s_beta.plant"

    with conn.cursor() as curr:
        curr.execute(query)
        row = curr.fetchone()

    return row["count"]


def get_avg_soil_moisture(conn: connect,
                          param: str,
                          current: datetime = datetime.now(timezone.utc)) -> tuple[int]:
    """Returns average soil moisture across all plants
    and change from previous minute."""

    query = f"""
            SELECT r.recording_taken, r.{param}
            FROM s_beta.recording AS r
            """

    with conn.cursor() as curr:
        curr.execute(query)
        rows = curr.fetchall()

    df = pd.DataFrame(rows)
    df['recording_taken'] = pd.to_datetime(df['recording_taken'], utc=True)

    avg = df[current - df['recording_taken']
             <= timedelta(minutes=1)][param].mean().round(2)
    avg_prev = df[(current - df['recording_taken'] <= timedelta(minutes=2)) &
                  (current - df['recording_taken'] > timedelta(minutes=1))][param].mean().round(2)

    return avg, round(avg-avg_prev, 2)


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    # DASHBOARD: PAGE SETTING
    st.set_page_config(page_title="LMNH Plant Dashboard", page_icon="🌿", layout="wide",
                       initial_sidebar_state="expanded", menu_items=None)

    # DASHBOARD: SIDEBAR
    st.sidebar.title(":rainbow[LMNH Plant Recordings Dashboard]")
    st.sidebar.subheader("Plant recordings, no better way to see 'em")

    plant_id_selected = get_filter_variables(conn)

    st.sidebar.subheader("Plant Summary", divider="rainbow")

    plant_name, scientific_name, origin = get_plant_details(
        conn, plant_id_selected)

    st.sidebar.write(f"Plant Name: {plant_name}")
    st.sidebar.write(f"Scientific Name: {scientific_name}")
    st.sidebar.write(f"Country, Location, Timezone: {origin}")

    # DASHBOARD: MAIN

    metrics = st.columns(3)
    with metrics[0]:
        total_plant_count = get_total_plant_count(conn)
        st.metric("total plant count", total_plant_count)
    with metrics[1]:
        soil_avg, soil_delta = get_avg_soil_moisture(conn, "soil_moisture")
        st.metric("avg soil moisture", soil_avg, soil_delta, "off")
    with metrics[2]:
        temp_avg, temp_delta = get_avg_soil_moisture(conn, "temperature")
        st.metric("avg temperature", temp_avg, temp_delta, "off")

    conn.close()
