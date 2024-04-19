# ETL pipeline for the LMNH Botanical Wing

## Description

Pipes data provided by the LMNH API into an RDS database. Performs some data cleaning to improve the quality
of the data.

### Extract

The LMNH Botanical Wing has 50 plants in their care and sensor data for each plant is available via an API. Endpoints
only exist for each plant, hence the extract script works asynchronously to fetch the data from all 50 endpoints.

### Transform

This script converts the raw data provided by the extract script into classes which represent the data tables of the
relational database. This script also performs some light data cleaning, including:
    - Capitalisation of plant names.
    - Stripping of whitespace and anomalous punctuation from plant names.
    - Separating botanist names into first and last names as required by the first normal form.
    - Validating scientific names for plant species.

### Load

Uploads transformed data to the database. Attempts to obtain the keys of existing entities in the database and uploads
the entities if they do not exist.

## Installation
1. Create and activate a new virtual environment.
2. Run `pip3 install -r requirements.txt` to install dependencies.
3. Create a '.env' file to store the necessary keys to connect to AWS RDS:
    - DB_HOST
    - DB_NAME
    - DB_PORT
    - DB_USER
    - DB_PASSWORD

## Testing
1. Install pytest using pip install pytest.
2. Run pytest . while in the pipeline directory.