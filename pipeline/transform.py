from __future__ import annotations

import re
from datetime import datetime

from entities import Recording, Botanist, Origin, Plant, Image

EXPECTED_KEYS = {"plant_id", "botanist", "name", "origin_location", "recording_taken"}


def transform(data: list[dict]) -> list[Recording]:
    recordings = []

    for item in data:
        if not item or not validate_keys(item):
            continue

        # Extract origin data
        origin_data = item.get("origin_location")
        origin = Origin(
            longitude=float(origin_data[0]),
            latitude=float(origin_data[1]),
            country_code=origin_data[3],
            place_name=origin_data[2],
            timezone=origin_data[4],
        )

        # Extract and clean plant data
        plant_name = item.get("name", "").strip(" ").strip(",").title()
        scientific_name: str | None = item.get("scientific_name", [None])[0]
        scientific_name = clean_scientific_name(scientific_name)

        plant = Plant(
            name=plant_name,
            id=item.get("plant_id"),
            scientific_name=scientific_name,
            origin=origin,
        )

        # Extract and clean botanist data
        botanist_data = item.get("botanist")
        first_name, last_name = split_full_name(botanist_data.get("name"))

        botanist = Botanist(
            email=botanist_data.get("email"),
            phone=botanist_data.get("phone"),
            first_name=first_name,
            last_name=last_name,
        )

        # Extract and clean image data
        image_data = item.get("images")
        if image_data and "upgrade_access.jpg" not in image_data.get("license_url"):
            image = Image(
                original_url=image_data.get("original_url"),
                license=image_data.get("license"),
                license_name=image_data.get("license_name"),
                license_url=image_data.get("license_url"),
            )
        else:
            image = None

        # Extract recording data
        last_watered = item.get("last_watered")
        if last_watered:
            try:
                last_watered = datetime.strptime(
                    last_watered, "%a, %d %b %Y %H:%M:%S %Z"
                ).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_watered = None

        recording = Recording(
            plant=plant,
            recording_taken=item.get("recording_taken"),
            last_watered=last_watered,
            soil_moisture=item.get("soil_moisture"),
            temperature=item.get("temperature"),
            botanist=botanist,
            image=image,
        )

        recordings.append(recording)

    return recordings


def validate_keys(data: dict) -> bool:
    return all([key in data.keys() for key in EXPECTED_KEYS])


def clean_scientific_name(text: str) -> str | None:
    """Clean a plant species scientific name. If the output is not a valid scientific name, returns None."""
    if not text:
        return None

    pattern = r"'[^']*'"

    # Use re.sub() to replace matched patterns with an empty string
    cleaned_text = re.sub(pattern, "", text).strip().title()

    if len(cleaned_text.split(" ")) != 2:
        return None

    return cleaned_text


def split_full_name(name: str) -> tuple[str, str]:
    first_name = name.split()[0].title()
    last_name = " ".join(name.split()[1:]).title()

    return first_name, last_name
