-- This file should contain all code required to create & seed database tables.

CREATE TABLE IF NOT EXISTS botanist (
    botanist_id SMALLINT UNIQUE GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(100) NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    PRIMARY KEY (botanist_id)
);

CREATE TABLE plant (
    plant_id SMALLINT UNIQUE NOT NULL,
    plant_name VARCHAR(30) NOT NULL,
    scientific_name VARCHAR(30),
    origin_id SMALLINT UNIQUE NOT NULL,
        FOREIGN KEY (origin_id) REFERENCES origin(origin_id),
    PRIMARY KEY (plant_id)
);

CREATE TABLE image (
    image_id BIGINT GENERATED ALWAYS AS IDENTITY,
    original_url TEXT,
    license SMALLINT,
    license_name VARCHAR(30),
    license_url TEXT,
    PRIMARY KEY (image_id)
);

CREATE TABLE recording (
    recording_id BIGINT GENERATED ALWAYS AS IDENTITY,
    plant_id SMALLINT UNIQUE NOT NULL,
        FOREIGN KEY (plant_id) REFERENCES plant(plant_id),
    recording_taken TIMESTAMPTZ NOT NULL,
    last_watered TIMESTAMPTZ,
    soil_moisture DECIMAL(8, 4) NOT NULL,
    temperature DECIMAL(8, 4) NOT NULL,
    image_id BIGINT UNIQUE NOT NULL,
        FOREIGN KEY (image_id) REFERENCES image(image_id),
    botanist_id SMALLINT UNIQUE NOT NULL,
        FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    PRIMARY KEY (recording_id)
);

CREATE TABLE origin (
    origin_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    longitude DECIMAL(8, 2) NOT NULL,
    latitude DECIMAL(8, 2) NOT NULL,
    place_name VARCHAR(20) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    timezone VARCHAR(20) NOT NULL,
    PRIMARY KEY (origin_id)
);