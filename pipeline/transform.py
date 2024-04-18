"""
Script containing functions to transform raw data from the plant API
into more suitable data structures so that it can be loaded into a database.
"""

from __future__ import annotations

import re
from datetime import datetime

from entities import Recording, Botanist, Origin, Plant, Image

EXPECTED_KEYS = {"plant_id", "botanist", "name", "origin_location", "recording_taken"}


def transform(data: list[dict]) -> list[Recording]:
    """Converts raw data from the plant API response into a list of Recordings."""
    recordings = []

    for item in data:
        if not item or not validate_keys(EXPECTED_KEYS, item):
            continue

        origin = transform_origin(item)

        plant = transform_plant(item, origin)

        botanist = transform_botanist(item)

        image = transform_image(item)

        recording = transform_recording(item, plant, botanist, image)

        recordings.append(recording)

    return recordings


def transform_origin(data: dict) -> Origin:
    """Extracts and transforms origin data from the API response."""
    origin = data.get("origin_location")
    return Origin(
        longitude=float(origin[0]),
        latitude=float(origin[1]),
        country_code=origin[3],
        place_name=origin[2],
        timezone=origin[4],
    )


def transform_plant(data: dict, origin: Origin) -> Plant:
    """Extracts and transforms plant data from the API response."""
    plant_name = data.get("name", "").strip(" ").strip(",").title()
    scientific_name: str | None = data.get("scientific_name", [None])[0]
    scientific_name = clean_scientific_name(scientific_name)

    return Plant(
        name=plant_name,
        id=data.get("plant_id"),
        scientific_name=scientific_name,
        origin=origin,
    )


def transform_botanist(data: dict) -> Botanist:
    """Extracts and transforms botanist data from the API response."""
    botanist_data = data.get("botanist")
    first_name, last_name = split_full_name(botanist_data.get("name"))

    return Botanist(
        email=botanist_data.get("email"),
        phone=botanist_data.get("phone"),
        first_name=first_name,
        last_name=last_name,
    )


def transform_image(data: dict) -> Image | None:
    """
    Extracts and transforms image data from the API response, returning None if it
    cannot be extracted.
    """
    image_data = data.get("images")
    if image_data and "upgrade_access.jpg" not in image_data.get("license_url"):
        return Image(
            original_url=image_data.get("original_url"),
            license=image_data.get("license"),
            license_name=image_data.get("license_name"),
            license_url=image_data.get("license_url"),
        )

    return None


def transform_recording(
    data: dict, plant: Plant, botanist: Botanist, image: Image
) -> Recording:
    """Extracts and transforms recording data from the API response."""
    last_watered = data.get("last_watered")
    if last_watered:
        try:
            last_watered = datetime.strptime(
                last_watered, "%a, %d %b %Y %H:%M:%S %Z"
            ).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            last_watered = None

    return Recording(
        plant=plant,
        recording_taken=data.get("recording_taken"),
        last_watered=last_watered,
        soil_moisture=data.get("soil_moisture"),
        temperature=data.get("temperature"),
        botanist=botanist,
        image=image,
    )


def validate_keys(expected_keys: set[str], data: dict) -> bool:
    """Returns true if all expected keys are present in the provided dictionary, otherwise False."""
    return all(key in data.keys() for key in expected_keys)


def clean_scientific_name(text: str) -> str | None:
    """
    Clean a plant species scientific name. If the output is not a valid scientific name,
    returns None.
    """
    if not text:
        return None

    pattern = r"'[^']*'"

    # Use re.sub() to replace matched patterns with an empty string
    cleaned_text = re.sub(pattern, "", text).strip().title()

    if len(cleaned_text.split(" ")) != 2:
        return None

    return cleaned_text


def split_full_name(name: str) -> tuple[str, str]:
    """Splits a full name into forename and surname, returning a tuple."""
    first_name = name.split()[0].title()
    last_name = " ".join(name.split()[1:]).title()

    return first_name, last_name
