import json


def get_test_file():
    with open("./test/result.json", "r") as file:
        return json.load(file)


if __name__ == "__main__":
    json = get_test_file()
    print(json[0])
for data in json:
    if data:
        botanist_email = data.get("botanist", {}).get("email", "No email")
        botanist_name = data.get("botanist", {}).get("name", "No name")
        botanist_phone = data.get("botanist", {}).get("phone", "No phone")

        images = data.get("images")
        if images:
            license_name = images.get("license_name", "No license name")
            medium_url = images.get("medium_url", "No URL provided")
            original_url = images.get("original_url", "No URL provided")
            regular_url = images.get("regular_url", "No URL provided")
            small_url = images.get("small_url", "No URL provided")
            thumbnail_url = images.get("thumbnail", "No URL provided")
        else:
            license_name = "None"
            medium_url = "None"
            original_url = "None"
            regular_url = "None"
            small_url = "None"
            thumbnail_url = "None"

        last_watered = data.get("last_watered", "Not recorded")
        plant_name = data.get("name", "Unnamed plant")
        origin_location = data.get("origin_location")
        if origin_location:
            lat = origin_location[0]
            lon = origin_location[1]

        plant_id = data.get("plant_id", -1)
        recording_taken = data.get("recording_taken", "No record")
        scientific_name = data.get("scientific_name", ["Unknown"])
        soil_moisture = data.get("soil_moisture", 0)
        temperature = data.get("temperature", 0)
