import json
import psycopg2

def get_test_file():
    with open('./test/result.json', 'r') as file:
        return json.load(file)
def transform(data:list[dict]) -> dict:

    tables = {'images':[],'recording':[],'botanist':[],'plant':[],'origin':[]}
    for id_, data in enumerate(json):
        if data:
            botanist_email = data.get('botanist', {}).get('email', 'No email')
            botanist_name = data.get('botanist', {}).get('name', 'No name')
            first_name = botanist_name.split(' ')[0]
            second_name = botanist_name.split(' ')[1]
            botanist_phone = data.get('botanist', {}).get('phone', 'No phone')

            
            images = data.get('images')
            if images:
                license_name = images.get('license_name', 'No license name')
                license_url = images.get('license_url', 'No license url')
                medium_url = images.get('medium_url', 'No URL provided')
                original_url = images.get('original_url', 'No URL provided')
                regular_url = images.get('regular_url', 'No URL provided')
                small_url = images.get('small_url', 'No URL provided')
                thumbnail_url = images.get('thumbnail', 'No URL provided')
                
            else:
                license_name = 'None'
                medium_url ='None'  
                original_url = 'None'
                regular_url = 'None'
                small_url = 'None'
                thumbnail_url ='None'
            

            last_watered = data.get('last_watered', 'Not recorded')
            plant_name = data.get('name', 'Unnamed plant')
            origin_location = data.get('origin_location')
            if origin_location:
                lat = origin_location[0]
                lon = origin_location[1]
                place_name = origin_location[2]
                country_code= origin_location[3]
                timezone= origin_location[4]


                
            plant_id = data.get('plant_id', -1)
            recording_taken = data.get('recording_taken', 'No record')
            scientific_name = data.get('scientific_name', ['Unknown'])
            soil_moisture = data.get('soil_moisture', 0)
            temperature = data.get('temperature', 0)
            tables['plant'].append(([(plant_name,id_,scientific_name)]))
            tables['image'].append((license_name,license_url,medium_url,original_url,regular_url,small_url, thumbnail_url))
            tables['recording'.append(plant_id,recording_taken,last_watered,soil_moisture,temperature)]
            tables['origin'].append((lon,lat,place_name,country_code,timezone))
            tables['botanist'].append((botanist_email,botanist_phone,botanist_phone,first_name,second_name))

    