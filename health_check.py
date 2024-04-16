"""
Python script that extracts recent (24hr) plant data from LMNH
and checks for anomalous readings, if present, sends an email using
SES
"""


def get_merged_data(conn):
    """Access short-term database to get merged data"""

    sql_query


df = pd.read()


list_of_plant_ids = df['name'].unique()

df.groupby('plant_id')['temp', 'moisture'].mean()

if __name__ == "__main__":
    ...
