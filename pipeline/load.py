from __future__ import annotations

from pymssql import Connection, Cursor

EXPECTED_KEYS = {"images", "recording", "botanist", "plant", "origin"}


def upload_data(data: dict, conn: Connection) -> None:
    if not validate_keys(data):
        ...

    cursor = conn.cursor()

    for i in range(0, len(data["origin"]) - 1):
        # Get ID of origin if exists, otherwise upload
        origin = data["origin"][i]
        origin_id = get_origin_id(cursor, origin)
        if origin_id is None:
            origin_id = upload_origin(conn, cursor, origin)

        # Get ID of plant if exists, otherwise upload
        plant = data["plant"][i]
        plant_id = get_plant_id(cursor, plant)
        if plant_id is None:
            upload_plant(conn, cursor, plant, origin_id)
            plant_id = plant[1]

        # Get ID of image if exists, otherwise upload
        image = data["images"][i]
        image_id = get_image_id(cursor, image)
        if image_id is None:
            image_id = upload_image(conn, cursor, image)

        # Get ID of botanist if exists, otherwise upload
        botanist = data["botanist"][i]
        botanist_id = get_botanist_id(cursor, botanist)
        if botanist_id is None:
            botanist_id = upload_botanist(conn, cursor, botanist)

        # Upload recording
        recording = data["recording"][i]
        upload_recording(conn, cursor, recording, plant_id, image_id, botanist_id)

    conn.commit()


def get_origin_id(cursor: Cursor, origin: tuple) -> int | None:
    cursor.execute(
        """
        SELECT origin_id
        FROM s_beta.origin
        WHERE longitude = %s
        AND latitude = %s;
        """,
        (origin[0], origin[1]),
    )

    res = cursor.fetchone()

    return res["origin_id"] if res else None


def upload_origin(conn: Connection, cursor: Cursor, origin: tuple) -> int:
    sql = """
                INSERT INTO s_beta.origin
                    ("longitude", "latitude", "place_name", "country_code", "timezone")
                VALUES 
                    (%s, %s, %s, %s, %s);
                """

    params = (origin[0], origin[1], origin[2], origin[3], origin[4])

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def get_plant_id(cursor: Cursor, plant: tuple) -> int | None:
    cursor.execute(
        """
        SELECT plant_id
        FROM s_beta.plant
        WHERE plant_id = %s
        """,
        (plant[1]),
    )

    res = cursor.fetchone()

    return res["plant_id"] if res else None


def upload_plant(conn: Connection, cursor: Cursor, plant: list, origin_id: int) -> None:
    sql = """
        INSERT INTO s_beta.plant
            ("plant_id", "plant_name", "scientific_name", "origin_id")
        VALUES 
            (%s, %s, %s, %s);
        """

    params = (plant[1], plant[0], plant[2], origin_id)

    cursor.execute(sql, params)

    conn.commit()


def get_image_id(cursor: Cursor, image: tuple) -> int | None:
    cursor.execute(
        """
        SELECT image_id
        FROM s_beta.image
        WHERE original_url = %s
        """,
        params=(image[2]),
    )

    res = cursor.fetchone()

    return res["image_id"] if res else None


def upload_image(conn: Connection, cursor: Cursor, image: tuple) -> int:
    sql = """
        INSERT INTO s_beta.image
            ("original_url", "license", "license_name", "license_url")
        VALUES 
            (%s, %s, %s, %s);
        """

    params = (image[2], image[3], image[0], image[1])

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def get_botanist_id(cursor: Cursor, botanist: tuple) -> int | None:
    cursor.execute(
        """
        SELECT botanist_id
        FROM s_beta.botanist
        WHERE email = %s
        AND phone_number = %s
        AND first_name = %s
        AND last_name = %s;
        """,
        params=(botanist[0], botanist[1], botanist[2], botanist[3]),
    )

    res = cursor.fetchone()

    return res["botanist_id"] if res else None


def upload_botanist(conn: Connection, cursor: Cursor, botanist: tuple) -> int:
    sql = """
            INSERT INTO s_beta.botanist
                ("email", "phone_number", "first_name", "last_name")
            VALUES 
                (%s, %s, %s, %s);
            """

    params = (botanist[0], botanist[1], botanist[2], botanist[3])

    cursor.execute(sql, params)

    conn.commit()

    return int(cursor.lastrowid)


def upload_recording(
    conn: Connection,
    cursor: Cursor,
    recording: tuple,
    plant_id: int,
    image_id: int,
    botanist_id: int,
) -> None:
    sql = """
        INSERT INTO s_beta.recording
            ("plant_id", "recording_taken", "last_watered", "soil_moisture", "temperature", "image_id", "botanist_id")
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s);
        """

    params = (
        plant_id,
        recording[1],
        recording[2],
        recording[3],
        recording[4],
        image_id,
        botanist_id,
    )

    conn.commit()

    cursor.execute(sql, params)


def validate_keys(data: dict) -> bool:
    return all([key in EXPECTED_KEYS for key in data.keys()])
