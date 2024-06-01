import sys
import boto3
from datetime import datetime
import logging

# Logging setup
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

QUERY_RESULTS_BUCKET = 's3://weather-data-prod-result-final/'
MY_DATABASE = 'weather-db'
SOURCE_PARQUET_TABLE_NAME = 'edmonton_weather_data_parquet_tbl'
NEW_PROD_PARQUET_TABLE_NAME = 'edmonton_weather_data_parquet_tbl_PROD'
NEW_PROD_PARQUET_TABLE_S3_BUCKET = 's3://weather-data-prod-final'

# create a string with the current UTC datetime
# convert all special characters to underscores
# this will be used in the table name and in the bucket path in S3 where the table is stored
DATETIME_NOW_INT_STR = str(datetime.now()).replace('-', '_').replace(' ', '_').replace(':', '_').replace('.', '_')

client = boto3.client('athena')

# Refresh the table
root.info('Starting Athena query execution...')
try:
    queryStart = client.start_query_execution(
        QueryString = f"""
        CREATE TABLE {NEW_PROD_PARQUET_TABLE_NAME}_{DATETIME_NOW_INT_STR} WITH
        (external_location='{NEW_PROD_PARQUET_TABLE_S3_BUCKET}/{DATETIME_NOW_INT_STR}/',
        format='PARQUET',
        write_compression='SNAPPY',
        partitioned_by = ARRAY['time'])
        AS

            SELECT
                   *
            FROM "{MY_DATABASE}"."{SOURCE_PARQUET_TABLE_NAME}"
            ;
            """,
            QueryExecutionContext={
                'Database': f'{MY_DATABASE}'
            },
            ResultConfiguration={'OutputLocation': f'{QUERY_RESULTS_BUCKET}'}
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

