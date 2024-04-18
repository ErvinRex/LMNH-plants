from dataclasses import dataclass
from typing import Optional


@dataclass
class Botanist:
    first_name: str
    last_name: str
    email: str
    phone: str


@dataclass
class Image:
    original_url: str
    license_name: str
    license_url: str
    license: int


@dataclass
class Origin:
    longitude: float
    latitude: float
    place_name: str
    country_code: str
    timezone: str


@dataclass
class Plant:
    name: str
    id: int
    origin: Origin
    scientific_name: Optional[str] = None


@dataclass
class Recording:
    plant: Plant
    recording_taken: str
    last_watered: str
    soil_moisture: float
    temperature: float
    botanist: Botanist
    image: Optional[Image] = None
