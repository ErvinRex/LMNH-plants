-- This file should contain all code required to create & seed database tables.

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'botanist' AND schema_id = SCHEMA_ID('s_beta'))
BEGIN
    CREATE TABLE s_beta.botanist (
        botanist_id INT IDENTITY(1,1) PRIMARY KEY,
        email VARCHAR(100) NOT NULL,
        phone_number VARCHAR(30) NOT NULL,
        first_name VARCHAR(20) NOT NULL,
        last_name VARCHAR(20) NOT NULL
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'origin' AND schema_id = SCHEMA_ID('s_beta'))
BEGIN
    CREATE TABLE s_beta.origin (
        origin_id INT IDENTITY(1,1) PRIMARY KEY,
        longitude DECIMAL(9, 6) NOT NULL,
        latitude DECIMAL(9, 6) NOT NULL,
        place_name VARCHAR(20) NOT NULL,
        country_code VARCHAR(2) NOT NULL,
        timezone VARCHAR(20) NOT NULL
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'plant' AND schema_id = SCHEMA_ID('s_beta'))
BEGIN
    CREATE TABLE s_beta.plant (
        plant_id INT PRIMARY KEY,
        plant_name VARCHAR(75) NOT NULL,
        scientific_name VARCHAR(75),
        origin_id INT NOT NULL,
            FOREIGN KEY (origin_id) REFERENCES s_beta.origin(origin_id) ON DELETE CASCADE
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'image' AND schema_id = SCHEMA_ID('s_beta'))
BEGIN
    CREATE TABLE s_beta.image (
        image_id BIGINT IDENTITY(1,1) PRIMARY KEY,
        original_url NVARCHAR(MAX),
        license SMALLINT,
        license_name VARCHAR(75),
        license_url NVARCHAR(MAX)
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'recording' AND schema_id = SCHEMA_ID('s_beta'))
BEGIN
    CREATE TABLE s_beta.recording (
        recording_id BIGINT IDENTITY(1,1) PRIMARY KEY,
        plant_id INT NOT NULL,
            FOREIGN KEY (plant_id) REFERENCES s_beta.plant(plant_id) ON DELETE CASCADE,
        recording_taken DATETIME2 NOT NULL,
        last_watered DATETIME2,
        soil_moisture DECIMAL(8, 4) NOT NULL,
        temperature DECIMAL(8, 4) NOT NULL,
        image_id BIGINT,
            FOREIGN KEY (image_id) REFERENCES s_beta.image(image_id) ON DELETE CASCADE,
        botanist_id INT NOT NULL,
            FOREIGN KEY (botanist_id) REFERENCES s_beta.botanist(botanist_id) ON DELETE CASCADE
    );
END;
