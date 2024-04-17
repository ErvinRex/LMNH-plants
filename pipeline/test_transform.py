import pytest
from transform import (
    clean_scientific_name,
    transform,
    validate_keys,
    Recording,
    Plant,
    Image,
    Origin,
    Botanist,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Chlorophytum comosum 'Vittatum'", "Chlorophytum Comosum"),
        ("Heliconia schiedeana 'Fire and Ice'", "Heliconia Schiedeana"),
        ("Gaillardia aestivalis", "Gaillardia Aestivalis"),
        ("Begonia 'Art Hodes'", None),
        ("Saintpaulia ionantha", "Saintpaulia Ionantha"),
    ],
)
def test_clean_scientific_name(text, expected):
    assert clean_scientific_name(text) == expected


def test_transform():
    test_data = [
        {
            "botanist": {
                "email": "email",
                "name": "fname lname",
                "phone": "phone",
            },
            "images": {
                "license": 45,
                "license_name": "name",
                "license_url": "lurl",
                "medium_url": "murl",
                "original_url": "ourl",
                "regular_url": "rurl",
                "small_url": "surl",
                "thumbnail": "thumb",
            },
            "last_watered": "Tue, 16 Apr 2024 14:03:04 GMT",
            "name": "Epipremnum aureum",
            "origin_location": [
                "-19.3",
                "-41.2",
                "Resplendor",
                "BR",
                "America/Sao_Paulo",
            ],
            "plant_id": 0,
            "recording_taken": "2024-04-17 10:56:19",
            "scientific_name": ["Epipremnum aureum"],
            "soil_moisture": 27.2,
            "temperature": 13.2,
        }
    ]

    expected = [
        Recording(
            plant=Plant(
                name="Epipremnum Aureum",
                scientific_name="Epipremnum Aureum",
                id=0,
                origin=Origin(
                    country_code="BR",
                    longitude=-19.3,
                    latitude=-41.2,
                    place_name="Resplendor",
                    timezone="America/Sao_Paulo",
                ),
            ),
            botanist=Botanist(
                first_name="Fname", last_name="Lname", email="email", phone="phone"
            ),
            last_watered="2024-04-16 14:03:04",
            recording_taken="2024-04-17 10:56:19",
            soil_moisture=27.2,
            temperature=13.2,
            image=Image(
                license=45, license_name="name", license_url="lurl", original_url="ourl"
            ),
        )
    ]

    assert transform(test_data) == expected


def test_validate_keys():
    test_data = {
        "botanist": {
            "email": "email",
            "name": "fname lname",
            "phone": "phone",
        },
        "images": {
            "license": 45,
            "license_name": "name",
            "license_url": "lurl",
            "medium_url": "murl",
            "original_url": "ourl",
            "regular_url": "rurl",
            "small_url": "surl",
            "thumbnail": "thumb",
        },
        "last_watered": "Tue, 16 Apr 2024 14:03:04 GMT",
        "name": "Epipremnum aureum",
        "origin_location": [
            "-19.3",
            "-41.2",
            "Resplendor",
            "BR",
            "America/Sao_Paulo",
        ],
        "plant_id": 0,
        "recording_taken": "2024-04-17 10:56:19",
        "scientific_name": ["Epipremnum aureum"],
        "soil_moisture": 27.2,
        "temperature": 13.2,
    }

    assert validate_keys(test_data)
