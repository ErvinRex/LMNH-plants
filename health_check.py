df = pd.read()


list_of_plant_ids = df['name'].unique()

df.groupby('plant_id')['temp', 'moisture'].mean()
