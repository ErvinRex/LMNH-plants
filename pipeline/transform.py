from datetime import datetime


def transform(data: list[dict]) -> dict:
    tables = {"images": [], "recording": [], "botanist": [], "plant": [], "origin": []}

    for id_, data in enumerate(data):
        if data:
            botanist_email = data.get("botanist", {}).get("email", None)
            botanist_name = data.get("botanist", {}).get("name", None)
            first_name = botanist_name.split(" ")[0]
            second_name = botanist_name.split(" ")[1]
            botanist_phone = data.get("botanist", {}).get("phone", None)

            images = data.get("images")
            if images:
                lic = images.get("license", None)
                license_name = images.get("license_name", None)[:29]
                license_url = images.get("license_url", None)
                original_url = images.get("original_url", None)
            else:
                lic = None
                license_name = None
                license_url = None
                original_url = None

            last_watered = data.get("last_watered", None)
            last_watered = datetime.strptime(
                last_watered, "%a, %d %b %Y %H:%M:%S %Z"
            ).strftime("%Y-%m-%d %H:%M:%S")
            plant_name = data.get("name", None)
            origin_location = data.get("origin_location", None)
            if origin_location:
                lat = origin_location[0]
                lon = origin_location[1]
                place_name = origin_location[2]
                country_code = origin_location[3]
                timezone = origin_location[4]

            plant_id = data.get("plant_id", None)
            recording_taken = data.get("recording_taken", None)
            scientific_name = data.get("scientific_name", None)
            if scientific_name:
                scientific_name = scientific_name[0]
            soil_moisture = data.get("soil_moisture", None)
            temperature = data.get("temperature", None)
            tables["plant"].append((plant_name, id_, scientific_name))
            tables["images"].append((license_name, license_url, original_url, lic))
            tables["recording"].append(
                (plant_id, recording_taken, last_watered, soil_moisture, temperature)
            )
            tables["origin"].append((lon, lat, place_name, country_code, timezone))
            tables["botanist"].append(
                (
                    botanist_email,
                    botanist_phone,
                    first_name,
                    second_name,
                )
            )

    return tables
