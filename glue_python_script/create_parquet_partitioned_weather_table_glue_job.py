import sys
import boto3
import logging

# Logging setup
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

client = boto3.client('athena')  # creating client to access AWS Athena service

SOURCE_TABLE_NAME = 'weather_weather_rawdata_bucket'  # source table created by Glue Crawler in our Glue Data Catalog for our source data
NEW_TABLE_NAME = 'edmonton_weather_data_parquet_tbl'  # new table to be created to include transformed data
NEW_TABLE_S3_BUCKET = 's3://weather-transformed-data-bucket/'  # new S3 bucket to store our transformed data
MY_DATABASE = 'weather-db'  # database in Glue Database to store Athena tables
QUERY_RESULTS_S3_BUCKET = 's3://weather-data-project-result-query/'  # S3 bucket used to store result

root.info('Starting Athena query execution...')
try:
    # Refresh the table
    queryStart = client.start_query_execution(
        QueryString=f"""
        CREATE TABLE {NEW_TABLE_NAME} WITH
        (external_location='{NEW_TABLE_S3_BUCKET}',
        format='PARQUET',
        write_compression='SNAPPY',
        partitioned_by = ARRAY['time'])
        AS

        SELECT
            latitude
            ,longitude
            ,timezone
            ,temperature_fahrenheit AS temp_F
            ,ROUND((temperature_fahrenheit - 32) * (5.0/9.0), 1) AS temp_C
            , CASE 
                WHEN day_or_night = 1 THEN 'day' ELSE 'night'
                END AS day_night_flag
            ,rain
            ,snowfall
            ,time_processed
            ,time
        FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"
        ;
        """,
        QueryExecutionContext={
            'Database': f'{MY_DATABASE}'
        },
        ResultConfiguration={'OutputLocation': f'{QUERY_RESULTS_S3_BUCKET}'}
    )

    root.info('Query started successfully, waiting for it to complete...')

    # possible states are 'QUEUED'|'RUNNING'|'SUCCEEDED'|'FAILED'|'CANCELLED'
    # List of final response states
    resp = ["FAILED", "SUCCEEDED", "CANCELLED"]

    while True:
        # Get the response
        response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

        # Check the status of the query
        state = response["QueryExecution"]["Status"]["State"]
        root.info(f'Athena query status: {state}')

        if state in resp:
            if state == 'FAILED':
                # If the query fails, exit and log the error message
                error_message = response["QueryExecution"]["Status"]["StateChangeReason"]
                root.error(f'Athena query failed: {error_message}')
                sys.exit(1)
            break  # Exit the loop if the query is in any final state (SUCCEEDED or CANCELLED)

    root.info('Athena query completed successfully.')

except Exception as e:
    root.error(f"An error occurred: {str(e)}")
    sys.exit(1)
