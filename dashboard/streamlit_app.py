"""
Python script for visualising and hosting a dashboard for LMNH plant data
"""

from os import environ as ENV, system, listdir
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from re import fullmatch
from dotenv import load_dotenv
from boto3 import client
from pymssql import connect
import pandas as pd
import altair as alt
import streamlit as st


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


# ========== FUNCTIONS: ST.SELECTIONS ==========
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


def get_timespan_slider(unit: str, span: int, key: str) -> int:
    """Returns timespan (by hours) slider for line graphs."""

    return st.select_slider(f"{unit}:",
                            options=list(range(span, 0, -1)),
                            value=2,
                            key=key)


# ========== FUNCTIONS: ST.METRICS ==========
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


# ========== FUNCTIONS: REAL-TIME DATA ==========
def get_realtime_df(conn: connect) -> pd.DataFrame:
    """Returns real-time data as a pd.DF."""

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

    return df


def get_realtime_graph(df: pd.DataFrame,
                       plant_id: int,
                       hours: int,
                       current: datetime = datetime.now(timezone.utc)) -> st.altair_chart:
    """Returns real-time data as a line graph."""

    df = df[(current - df["recording_taken"] <= timedelta(hours=hours)) &
            (df["plant_id"] == plant_id) &
            (df["soil_moisture"] >= 0)]

    if hours > 3:
        df = df.set_index("recording_taken")
        df = df.groupby("plant_id").resample(
            "H", include_groups=False).mean().reset_index()

    base = alt.Chart(df).encode(
        x=alt.X("recording_taken:T", title="time", axis=alt.Axis(format='%H:%M'))).properties(height=250)
    soil = base.mark_line(stroke="turquoise").encode(
        alt.Y("soil_moisture", title="soil moisture"))
    temp = base.mark_line(stroke="orangered").encode(
        alt.Y("temperature").title("temperature", titleColor="red"))
    graph = alt.layer(soil, temp
                      ).resolve_scale(y='independent'
                                      ).configure_axisLeft(titleColor='turquoise',
                                                           labelColor="turquoise"
                                                           ).configure_axisRight(titleColor='orangered',
                                                                                 labelColor="orangered")

    return graph


def get_std(row: dict, df: pd.DataFrame, col: str) -> int:
    """Compare minutely value to mean of past hour;
    Returns std."""

    last_hour = pd.Timestamp(datetime.now(timezone.utc)-timedelta(hours=1))
    last_hour_vals = df[(df["plant_id"] == row["plant_id"]) &
                        (df["recording_taken"] >= last_hour)][col]

    mean = last_hour_vals.mean()
    std = last_hour_vals.std()

    nstd = (row[col] - mean) / std

    return nstd


def get_realtime_stds(df: pd.DataFrame,
                      current: datetime = datetime.now(timezone.utc)):
    """Returns top real-time standard deviations as a bar chart."""

    df = df[(current - df["recording_taken"]) <= timedelta(hours=1)]

    df["soil_moisture_nstd"] = df.apply(get_std,
                                        args=(df, "soil_moisture"),
                                        axis=1)
    df["temperature_nstd"] = df.apply(get_std,
                                      args=(df, "temperature"),
                                      axis=1)

    df = df[(current - df["recording_taken"]) <= timedelta(minutes=1)]

    df["total_nstd"] = df["soil_moisture_nstd"].abs() + \
        df["temperature_nstd"].abs()

    df = df.sort_values("total_nstd", ascending=False).head(10)

    chart = alt.Chart(df).transform_fold(
        ["soil_moisture_nstd", "temperature_nstd"],
        as_=["metric", "stds"]
    ).mark_bar().encode(
        y=alt.Y('plant_id:N',
                title="plant id",
                sort=alt.EncodingSortField(field='total_nstd',
                                           order='descending')),
        x=alt.X('stds:Q',
                axis=alt.Axis(title='standard deviation',
                              orient='top')),
        color=alt.Color('metric:N',
                        legend=None,
                        scale=alt.Scale(domain=['soil_moisture_nstd', 'temperature_nstd'],
                                        range=['turquoise', 'orangered'])),
        order=alt.Order("stds:Q", sort='descending')
    )

    return chart


# ========== FUNCTIONS: HISTORICAL DATA =========
def check_within_timeframe(month: int,
                           filename: str,
                           current: datetime = datetime.today()) -> bool:

    split = [int(num) for num in filename.split("/")[:3]]
    file_date = datetime(split[0], split[1], split[2])

    return file_date >= (current - relativedelta(month=month))


def get_longterm_csv_names(client: client,
                           month: int,
                           bucket: str = "late-ordovician") -> list[str]:
    """Returns a list of filenames of summary/anomalies.csv
    within a given time span."""

    filenames = [obj["Key"] for obj
                 in client.list_objects(Bucket=bucket)["Contents"]
                 if bool(fullmatch(r".{11}(?:summary|anomalies).csv", obj["Key"]))
                 and check_within_timeframe(month, obj["Key"])]

    return filenames


def download_longterm_csvs(client: client,
                           month: int,
                           bucket: str = "late-ordovician",
                           directory: str = "data") -> None:
    """Downloads a list of objects from an S3 bucket.
    Returns nothing."""

    filenames = get_longterm_csv_names(client, month, bucket)

    system(f"mkdir {directory}")

    for filename in filenames:
        path = f"{directory}/{filename.replace("/", "_")}"
        client.download_file(bucket, filename, path)


def combine_csvs(info: str, directory: str = "data") -> pd.DataFrame:
    """Return CSVs with the same type of data as pd.DF."""

    files = listdir(directory)
    csvs = [pd.read_csv(f"{directory}/{file}")
            for file in files
            if info in file]
    df = pd.concat(csvs, ignore_index=True)
    return df


def get_historical_graph(df: pd.DataFrame,
                         plant_id: int,
                         current: datetime = datetime.now(timezone.utc)) -> st.altair_chart:
    """Returns historical data as a line graph."""


if __name__ == "__main__":

    load_dotenv()

    connection = get_db_connection(ENV)

    S3 = client('s3',
                aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

    # ===== DASHBOARD: PAGE SETTING =====
    st.set_page_config(page_title="LMNH Plant Dashboard", page_icon="🌿", layout="wide",
                       initial_sidebar_state="expanded", menu_items=None)

    # ===== DASHBOARD: SIDEBAR =====
    st.sidebar.title(":rainbow[LMNH Plant Recordings Dashboard]")
    st.sidebar.subheader("Plant recordings, no better way to see 'em")

    with st.sidebar:
        sidebar_plant_id = get_plant_selection(connection, "sidebar_plant_id")

    st.sidebar.subheader("Plant Summary", divider="rainbow")

    plant_name, scientific_name, origin = get_plant_details(
        connection, sidebar_plant_id)

    st.sidebar.write(f"Plant Name: {plant_name}")
    st.sidebar.write(f"Scientific Name: {scientific_name}")
    st.sidebar.write(f"Country, Location, Timezone: {origin}")

    # ===== DASHBOARD: MAIN =====
    basic, stds = st.columns([.7, .3], gap="large")

    with basic:
        metrics = st.columns(3)
        with metrics[0]:
            total_plant_count = get_total_plant_count(connection)
            st.metric("total plant count", total_plant_count)
        with metrics[1]:
            soil_avg, soil_delta = get_avg_metric(connection, "soil_moisture")
            st.metric("avg soil moisture", soil_avg, soil_delta, "off")
        with metrics[2]:
            temp_avg, temp_delta = get_avg_metric(connection, "temperature")
            st.metric("avg temperature", temp_avg, temp_delta, "off")

        st.subheader("Real-time Soil Moisture and Temperature")
        realtime_df = get_realtime_df(connection)
        realtime_col = st.columns([.15, .85], gap="medium")
        with realtime_col[0]:
            realtime_plant_id = get_plant_selection(
                connection, "realtime_plant_id")
            realtime_timespan = get_timespan_slider(
                "hours", 12, "realtime_timespan")
        with realtime_col[1]:
            realtime_graph = get_realtime_graph(
                realtime_df, realtime_plant_id, realtime_timespan)
            st.altair_chart(
                realtime_graph,
                use_container_width=True
            )

        st.subheader("Historical Soil Moisture and Temperature")
        historical = st.columns([.15, .85], gap="medium")
        with historical[0]:
            historical_plant_id = get_plant_selection(
                connection, "historical_plant_id")
            historical_timespan = get_timespan_slider(
                "months", 12, "historical_timespan")
        with historical[1]:
            download_longterm_csvs(S3, historical_timespan)
            summary_df = combine_csvs("summary")
            anomalies_df = combine_csvs("anomalies")

            st.write(summary_df)

    with stds:
        st.subheader("Top Real-time SD")
        realtime_std = get_realtime_stds(realtime_df)
        st.altair_chart(realtime_std, use_container_width=True)

        st.subheader("Top Historical SD")
        st.write(anomalies_df)

    connection.close()
