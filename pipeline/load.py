"""Loads transformed data into a RDS database."""

from __future__ import annotations

from pymssql import Connection, Cursor

from entities import Recording, Origin, Plant, Image, Botanist


def upload_data(data: list[Recording], conn: Connection) -> None:
    """
    Uploads transformed data to the specified database. Tries to obtain the keys of
    existing entities in the database; if it does not exist, uploads the entity.
    """
    cursor = conn.cursor()

    for item in data:
        origin_id = get_origin_id(cursor, item.plant.origin)
        if origin_id is None:
            origin_id = upload_origin(conn, cursor, item.plant.origin)

        plant_id = get_plant_id(cursor, item.plant)
        if plant_id is None:
            upload_plant(conn, cursor, item.plant, origin_id)

        if item.image:
            image_id = get_image_id(cursor, item.image)
            if image_id is None:
                image_id = upload_image(conn, cursor, item.image)
        else:
            image_id = None

        botanist_id = get_botanist_id(cursor, item.botanist)
        if botanist_id is None:
            botanist_id = upload_botanist(conn, cursor, item.botanist)

        upload_recording(conn, item, item.plant.id, image_id, botanist_id)

    conn.close()


def get_origin_id(cursor: Cursor, origin: Origin) -> int | None:
    """
    Attempts to match the origin object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cursor.execute(
        """
        SELECT origin_id
        FROM s_beta.origin
        WHERE longitude = %s
        AND latitude = %s;
        """,
        (origin.longitude, origin.latitude),
    )

    res = cursor.fetchone()

    return res["origin_id"] if res else None


def upload_origin(conn: Connection, cursor: Cursor, origin: Origin) -> int:
    """Uploads an origin object to the database, returning the new ID of the uploaded entity."""
    sql = """
                INSERT INTO s_beta.origin
                    ("longitude", "latitude", "place_name", "country_code", "timezone")
                VALUES 
                    (%s, %s, %s, %s, %s);
                """

    params = (
        origin.longitude,
        origin.latitude,
        origin.place_name,
        origin.country_code,
        origin.timezone,
    )

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def get_plant_id(cursor: Cursor, plant: Plant) -> int | None:
    """
    Attempts to match the plant object to an existing entity in the database and
    extract its primary key. Otherwise, returns None.
    """
    cursor.execute(
        """
        SELECT plant_id
        FROM s_beta.plant
        WHERE plant_id = %s
        """,
        plant.id,
    )

    res = cursor.fetchone()

    return res["plant_id"] if res else None


def upload_plant(
    conn: Connection, cursor: Cursor, plant: Plant, origin_id: int
) -> None:
    """Uploads a plant object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO s_beta.plant
            ("plant_id", "plant_name", "scientific_name", "origin_id")
        VALUES 
            (%s, %s, %s, %s);
        """

    params = (plant.id, plant.name, plant.scientific_name, origin_id)

    cursor.execute(sql, params)

    conn.commit()


def get_image_id(cursor: Cursor, image: Image) -> int | None:
    """
    Attempts to match the image object to an existing entity in the database and
    extract its primary key. Otherwise, returns None.
    """
    cursor.execute(
        """
        SELECT image_id
        FROM s_beta.image
        WHERE original_url = %s
        """,
        params=image.original_url,
    )

    res = cursor.fetchone()

    return res["image_id"] if res else None


def upload_image(conn: Connection, cursor: Cursor, image: Image) -> int:
    """Uploads an image object to the database, returning the new ID of the uploaded entity."""
    sql = """
        INSERT INTO s_beta.image
            ("original_url", "license", "license_name", "license_url")
        VALUES 
            (%s, %s, %s, %s);
        """

    params = (image.original_url, image.license, image.license_name, image.license_url)

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def get_botanist_id(cursor: Cursor, botanist: Botanist) -> int | None:
    """
    Attempts to match the botanist object to an existing entity in the database and
    extract its primary key. Otherwise, returns None.
    """
    cursor.execute(
        """
        SELECT botanist_id
        FROM s_beta.botanist
        WHERE email = %s
        AND phone_number = %s
        AND first_name = %s
        AND last_name = %s;
        """,
        params=(
            botanist.email,
            botanist.phone,
            botanist.first_name,
            botanist.last_name,
        ),
    )

    res = cursor.fetchone()

    return res["botanist_id"] if res else None


def upload_botanist(conn: Connection, cursor: Cursor, botanist: Botanist) -> int:
    """Uploads a botanist object to the database, returning the new ID of the uploaded entity."""
    sql = """
            INSERT INTO s_beta.botanist
                ("email", "phone_number", "first_name", "last_name")
            VALUES 
                (%s, %s, %s, %s);
            """

    params = (botanist.email, botanist.phone, botanist.first_name, botanist.last_name)

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def upload_recording(
    conn: Connection,
    recording: Recording,
    plant_id: int,
    image_id: int,
    botanist_id: int,
) -> None:
    """Uploads a recording object to the database."""
    sql = """
        INSERT INTO s_beta.recording
            ("plant_id", "recording_taken", "last_watered", "soil_moisture", "temperature", "image_id", "botanist_id")
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s);
        """

    params = (
        plant_id,
        recording.recording_taken,
        recording.last_watered,
        recording.soil_moisture,
        recording.temperature,
        image_id,
        botanist_id,
    )

    conn.commit()

    conn.cursor().execute(sql, params)
