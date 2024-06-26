"""
Python script that extracts recent (24hr) plant data from LMNH
and checks for anomalous readings, if present, sends an email using
SES
"""

from os import environ as ENV
from datetime import datetime, timedelta, timezone

import pandas as pd
from dotenv import load_dotenv
from pymssql import connect

from boto3 import client


def handler(event, context) -> dict:
    """This function makes the lambda function work"""

    conn = get_db_connection(ENV)
    df = get_df(conn)
    load_dotenv()
    moist_df = get_anomolous_column(df, "soil_moisture")
    temp_df = get_anomolous_column(df, "temperature")
    missing_ids = get_missing_values(df)

    moist_html = (
        moist_df.to_html()
        if not moist_df.empty
        else "<p>No moisture anomalies found.</p>"
    )
    temp_html = (
        temp_df.to_html()
        if not temp_df.empty
        else "<p>No temperature anomalies found.</p>"
    )
    missing_html = (
        f"<h3>Missing plant IDs in the last hour: {missing_ids}</h3>"
        if missing_ids
        else "<p>All plant IDs reported in the last hour.</p>"
    )

    combined_html = f"""
    <html>
        <body>
            {missing_html}
            <div style='display: table; width: 100%;'>
                <div style='display: table-cell; padding: 10px;'>
                    <h2>Anomalous Moisture Readings</h2>
                    {moist_html}
                </div>
                <div style='display: table-cell; padding: 10px;'>
                    <h2>Anomalous Temperature Readings</h2>
                    {temp_html}
                </div>
            </div>
        </body>
    </html>
    """

    if not moist_df.empty or not temp_df.empty or missing_ids:
        ses_client = client(
            "ses",
            aws_access_key_id=ENV["AWS_K"],
            aws_secret_access_key=ENV["AWS_SKEY"],
            region_name="eu-west-2",
        )
        send_email(ses_client, combined_html)

    return {
        "statusCode": 200,
        "body": "Processing complete. Email sent if anomalies were found.",
    }


def get_db_connection(config: dict) -> client:
    """Returns database connection."""

    return connect(
        server=config["DB_HOST"],
        port=config["DB_PORT"],
        user=config["DB_USER"],
        database=config["DB_NAME"],
        password=config["DB_PASSWORD"],
        as_dict=True,
    )


def get_df(conn: connect) -> pd.DataFrame:
    """Returns a Dataframe of the database"""

    query = """
            SELECT *
            FROM s_beta.recording AS r

            """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return pd.DataFrame(rows)


def send_email(sesclient: client, html: str) -> None:
    """Sends email using BOTO3"""

    sesclient.send_email(
        Source="trainee.dominic.chambers@sigmalabs.co.uk",
        Destination={
            "ToAddresses": [
                "trainee.ervin.rexhepi@sigmalabs.co.uk",
                "trainee.adam.osullivan@sigmalabs.co.uk",
                "trainee.dominic.chambers@sigmalabs.co.uk",
            ]
        },
        Message={
            "Subject": {"Data": "WE FOUND ANOMOLIES IN YOUR PLANT DATA. URGENT"},
            "Body": {"Text": {"Data": "HELLO FROM BOTO3"}, "Html": {"Data": html}},
        },
    )


def get_anomolous_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """This function returns any anomolies in a specific column over the last hour
    we assume that any anomolies are 2.5 standard deviations above or below the mean."""

    last_hour = pd.Timestamp(datetime.now(timezone.utc) - timedelta(hours=1))
    df["recording_taken"] = pd.to_datetime(df["recording_taken"], utc=True)
    df_in_last_hour = df[(df["recording_taken"] >= last_hour)]
    mean = df.groupby("plant_id")[column].mean().reset_index()
    std = df.groupby("plant_id")[column].std().reset_index()
    merged_df = pd.merge(mean, std, on="plant_id").rename(
        columns={f"{column}_x": "mean", f"{column}_y": "std"}
    )
    merged_df["anomolous +"] = merged_df["mean"] + merged_df["std"].apply(
        lambda x: x * 2.5
    )
    merged_df["anomolous -"] = merged_df["mean"] - merged_df["std"].apply(
        lambda x: x * 2.5
    )
    merge_2 = pd.merge(merged_df, df_in_last_hour, on="plant_id")
    merge_2 = merge_2[
        merge_2.apply(
            lambda x: (x["anomolous -"] <= x[column]) & (x[column] <= x["anomolous +"])
            is False,
            axis=1,
        )
    ]
    return merge_2[["plant_id", column]]


def get_missing_values(df: pd.DataFrame) -> set:
    """If any plants did not have a reading in the past hour we notify the stakeholders."""

    last_hour = pd.Timestamp(datetime.now(timezone.utc) - timedelta(hours=1))
    df["recording_taken"] = pd.to_datetime(df["recording_taken"], utc=True)
    df_in_last_hour = df[(df["recording_taken"] >= last_hour)]
    values_in_hour = set(df_in_last_hour["plant_id"].unique().tolist())
    expected_values = set(range(51))
    ids_not_found = expected_values - values_in_hour
    return ids_not_found
