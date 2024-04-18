"""
Python script for visualising and hosting a dashboard for LMNH plant data
"""

from os import environ as ENV
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import pandas as pd
import altair as alt
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


def get_plant_selection(conn: connect, key: str) -> int:
    """Returns the filter variables for filtering charts from streamlit multi-select"""

    with conn.cursor() as curr:
        query = "SELECT plant_id, plant_name FROM s_beta.plant"
        curr.execute(query, )
        rows = curr.fetchall()
    plant_ids = [plant_id.get('plant_id') for plant_id in rows]
    plant_id_selected = st.selectbox(
        "plant id:", plant_ids, key=key)

    return plant_id_selected


def get_timespan_slider(conn: connect, key: str) -> int:
    """Returns timespan (by hours) slider for line graphs."""

    return st.select_slider("time span (hours):",
                            options=list(range(5, 0, -1)),
                            value=2,
                            key=key)


def get_plant_details(conn: connect, plant_id_selected: int) -> tuple:
    """Returns the relevant plant_id details to be displayed."""

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

    with conn.cursor() as curr:
        query = "SELECT COUNT(plant_id) AS count FROM s_beta.plant"
        curr.execute(query)
        row = curr.fetchone()

    return row["count"]


def get_avg_metric(conn: connect,
                   metric: str,
                   current: datetime = datetime.now(timezone.utc)) -> tuple[int]:
    """Returns average soil moisture across all plants
    and change from previous minute."""

    with conn.cursor() as curr:
        query = f"""
            SELECT r.recording_taken, r.{metric}
            FROM s_beta.recording AS r
            """
        curr.execute(query)
        rows = curr.fetchall()

    df = pd.DataFrame(rows)
    df['recording_taken'] = pd.to_datetime(df['recording_taken'], utc=True)

    avg = df[current - df['recording_taken']
             <= timedelta(minutes=1)][metric].mean()
    avg_prev = df[(current - df['recording_taken'] <= timedelta(minutes=2)) &
                  (current - df['recording_taken'] > timedelta(minutes=1))][metric].mean()

    return round(avg), round(avg-avg_prev, 2)


def get_realtime_graph(conn: connect,
                       plant_id: int,
                       hours: int,
                       current: datetime = datetime.now(timezone.utc)) -> st.altair_chart:
    """Returns real-time data as a line graph."""

    with conn.cursor() as curr:
        query = f"""
            SELECT r.recording_taken, r.plant_id, soil_moisture, temperature
            FROM s_beta.recording AS r
            """
        curr.execute(query)
        rows = curr.fetchall()

    df = pd.DataFrame(rows)
    df['recording_taken'] = pd.to_datetime(df['recording_taken'], utc=True)
    df = df.astype({"soil_moisture": "float64",
                    "temperature": "float64"})

    df = df[(current - df["recording_taken"] <= timedelta(hours=hours)) &
            (df["plant_id"] == plant_id) &
            (df["soil_moisture"] >= 0)]

    base = alt.Chart(df).encode(
        x=alt.X("recording_taken", title="time"))

    soil = base.mark_line(stroke="chartreuse").encode(
        alt.Y("soil_moisture", title="soil moisture"))

    temp = base.mark_line(stroke="orangered").encode(
        alt.Y("temperature").title("temperature", titleColor="red"))

    graph = alt.layer(soil, temp
                      ).resolve_scale(y='independent'
                                      ).configure_axisLeft(titleColor='chartreuse'
                                                           ).configure_axisRight(titleColor='yellow')

    return graph


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    # ===== DASHBOARD: PAGE SETTING =====
    st.set_page_config(page_title="LMNH Plant Dashboard", page_icon="🌿", layout="wide",
                       initial_sidebar_state="expanded", menu_items=None)

    # ===== DASHBOARD: SIDEBAR =====
    st.sidebar.title(":rainbow[LMNH Plant Recordings Dashboard]")
    st.sidebar.subheader("Plant recordings, no better way to see 'em")

    with st.sidebar:
        sidebar_plant_id = get_plant_selection(conn, "sidebar_plant_id")

    st.sidebar.subheader("Plant Summary", divider="rainbow")

    plant_name, scientific_name, origin = get_plant_details(
        conn, sidebar_plant_id)

    st.sidebar.write(f"Plant Name: {plant_name}")
    st.sidebar.write(f"Scientific Name: {scientific_name}")
    st.sidebar.write(f"Country, Location, Timezone: {origin}")

    # ===== DASHBOARD: MAIN =====
    basic, stds = st.columns([.7, .3])

    with basic:
        metrics = st.columns(3)
        with metrics[0]:
            total_plant_count = get_total_plant_count(conn)
            st.metric("total plant count", total_plant_count)
        with metrics[1]:
            soil_avg, soil_delta = get_avg_metric(conn, "soil_moisture")
            st.metric("avg soil moisture", soil_avg, soil_delta, "off")
        with metrics[2]:
            temp_avg, temp_delta = get_avg_metric(conn, "temperature")
            st.metric("avg temperature", temp_avg, temp_delta, "off")

        realtime = st.columns([.15, .85])
        with realtime[0]:
            realtime_plant_id = get_plant_selection(
                conn, "realtime_plant_id")
            realtime_timespan = get_timespan_slider(
                conn, "realtime_timespan")
        with realtime[1]:
            realtime_graph = get_realtime_graph(
                conn, realtime_plant_id, realtime_timespan)
            st.altair_chart(
                realtime_graph,
                use_container_width=True
            )

        historical = st.columns([.15, .85])
        with historical[0]:
            historical_plant_id = get_plant_selection(
                conn, "historical_plant_id")
            historical_timespan = get_timespan_slider(
                conn, "historical_timespan")
        with historical[1]:
            pass

    with stds:
        pass

    conn.close()
