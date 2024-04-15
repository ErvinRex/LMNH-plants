"""
Python script that extracts recent (24hr) plant data from LMNH
and checks for anomalous readings, if present, sends an email using
SES
"""

df = pd.read()


list_of_plant_ids = df['name'].unique()

df.groupby('plant_id')['temp', 'moisture'].mean()

if __name__ == "__main__":
    ...
