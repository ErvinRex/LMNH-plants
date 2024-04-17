"""
Python script that extracts recent (24hr) plant data from LMNH
and checks for anomalous readings, if present, sends an email using
SES
"""
import pandas as pd
from datetime import datetime,timedelta

def get_mock_data():
    return pd.read_csv('./test/plant_recordings.csv')



def get_recording_data(conn):
    """Access short-term database to get merged data"""
    pass



def is_healthy_temp(df:pd.DataFrame) -> bool:
    now = pd.Timestamp(datetime.now())
    last_hour = pd.Timestamp(datetime.now() - timedelta(hours=1))
    df_in_last_hour = df[df['recording_taken'].apply(lambda x : last_hour<= pd.Timestamp(x)<=now)]
    mean_temperature = df.groupby('plant_id')['temperature'].mean().reset_index()
    std_temperature = df.groupby('plant_id')['temperature'].std().reset_index()
    merged_df = pd.merge(mean_temperature,std_temperature,on='plant_id').rename(columns={'temperature_x':'mean','temperature_y':'std'})
    merged_df['anomolous +'] =  merged_df['mean'] + merged_df['std'].apply(lambda x: x*1.5) 
    merged_df['anomolous -'] = merged_df['mean'] - merged_df['std'].apply(lambda x: x*1.5)
    merge_2 = pd.merge(merged_df,df_in_last_hour,on='plant_id')
    merge_2 = merge_2.apply(lambda x: (x['anomolous -'] <= x['temperature']) & (x['temperature'] <= x['anomolous +']), axis=1).tolist()

    return False in merge_2

if __name__ == "__main__":
    df = get_mock_data()
    print(is_healthy_temp(df))                   




