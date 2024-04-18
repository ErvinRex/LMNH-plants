# ========== IMPORTS ==========
from os import environ as ENV
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pymssql import connect
import pandas as pd
from boto3 import client


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


def get_data(conn: connect) -> pd.DataFrame:
    """Returns a Dataframe of method data from database."""

    query = """ 
            SELECT *
            FROM s_beta.recording AS r
            FULL JOIN s_beta.plant AS p
                ON r.plant_id = p.plant_id
            """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    df = pd.DataFrame(rows)[
        ["recording_taken", "plant_id", "plant_name", "scientific_name", "soil_moisture", "temperature"]]

    df = df.astype({"soil_moisture": "float64",
                    "temperature": "float64"})
    df['recording_taken'] = pd.to_datetime(df['recording_taken'], utc=True)

    return df


def get_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Gets 1 mean per parameter per plant.
    Returns pd.DF."""

    df = df.drop(columns=["recording_taken"])

    df = df.groupby(["plant_id", "plant_name", "scientific_name"], as_index=False
                    ).agg(["mean", "std", "min", "max"]
                          ).droplevel(1, axis=1)

    df.columns = ['plant_id', 'plant_name', 'scientific_name'] + \
        [param+"_"+metric
         for param in ['soil_moisture', 'temperature']
         for metric in ["mean", "std", "min", "max"]]

    return df


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


def get_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Gets rows with values 2.5std away from mean.
    Returns pd.DF."""

    df["soil_moisture_nstd"] = df.apply(get_std,
                                        args=(data, "soil_moisture"),
                                        axis=1)
    df["temperature_nstd"] = df.apply(get_std,
                                      args=(df, "temperature"),
                                      axis=1)

    df = df[(df["soil_moisture_nstd"] <= -2.5) |
            (df["soil_moisture_nstd"] >= 2.5) |
            (df["temperature_nstd"] <= -2.5) |
            (df["temperature_nstd"] >= 2.5)]

    return df


def upload_object(client: client,
                  file: str,
                  bucket: str = "late-ordovician",
                  date: datetime = datetime.now()) -> None:
    """Upload file to S3 bucket.
    Returns nothing."""

    key = date.strftime("%Y/%m/%d/") + file

    client.upload_file(file, bucket, key)


def reset_recording(conn: connect) -> None:
    """Drops and recreates table `recording` in database."""

    drop = "DROP TABLE s_beta.recording"
    create = """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'recording' AND schema_id = SCHEMA_ID('s_beta'))
            BEGIN
                CREATE TABLE s_beta.recording (
                    recording_id BIGINT IDENTITY(1,1) PRIMARY KEY,
                    plant_id INT NOT NULL,
                        FOREIGN KEY (plant_id) REFERENCES s_beta.plant(plant_id) ON DELETE CASCADE,
                    recording_taken DATETIME2 NOT NULL,
                    last_watered DATETIME2,
                    soil_moisture DECIMAL(8, 4) NOT NULL,
                    temperature DECIMAL(8, 4) NOT NULL,
                    image_id BIGINT,
                        FOREIGN KEY (image_id) REFERENCES s_beta.image(image_id) ON DELETE CASCADE,
                    botanist_id INT NOT NULL,
                        FOREIGN KEY (botanist_id) REFERENCES s_beta.botanist(botanist_id) ON DELETE CASCADE
                );
            END;
            """

    with conn.cursor() as cur:
        cur.execute(drop)
        cur.execute(create)
        conn.commit()


if __name__ == "__main__":

    # ===== connections =====
    load_dotenv()

    connection = get_db_connection(ENV)

    S3 = client('s3',
                aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

    # ===== extract data =====
    data = get_data(connection)

    # ===== transform data =====
    summary = get_summary(data)
    anomalies = get_anomalies(data)

    # ===== load data =====
    summary.to_csv("summary.csv", index=False)
    anomalies.to_csv("anomalies.csv", index=False)

    upload_object(S3, "summary.csv")
    upload_object(S3, "anomalies.csv")

    # ===== reset 24h recordings =====
    reset_recording(connection)
