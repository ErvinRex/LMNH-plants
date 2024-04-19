# Long-term (Process & Load)

## Description

A python pipeline that for all data >= 24 hours in the RDS, uploads a shortened summary version of recording data for each plant to an S3 bucket on AWS, separated by day and hour for easy accessibility  

### Longterm

1. Connect to `RDS` storing 24hr plant recording data every day.
2. Retrieve cleaned and formatted recording data for each plant.
3. Create summarised (to hour) of recordings for each plant.
4. Detect and generate anomalies recordings for each plant
5. Upload summarised and anaomalies `csv` to an `S3` bucket on `AWS`.

## Installation

## Installation/Setup Instructions

*Python3* dependant scripts

1. If running locally on a Mac-machine rather than terraforming, please go to the `bash_commands` folder and run `bash download_pymssql.sh` in your terminal.
2. Create and activate a new virtual environment.
3. Run 'pip3 install -r requirements.txt' to install dependencies.
4. Create a '.env' file to store the necessary keys to connect to AWS RDS and S3 Bucket.
    For the S3 Bucket:
    - AWS_KEY
    - AWS_SKEY

    For the AWS RDS:
    - 'DATABASE_NAME'
    - 'DATABASE_USER'
    - 'DATABASE_PASSWORD'
    - 'DATABASE_IP'
    - 'DATABASE_PORT'

5. Create a 'terraform.tfvars' file - check terraform readme for more information.