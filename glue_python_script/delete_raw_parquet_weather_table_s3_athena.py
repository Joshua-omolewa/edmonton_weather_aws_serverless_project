# author: Joshua Omolewa
import sys
import json
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

# replace these with the names from your environment
BUCKET_TO_DEL = 'weather-transformed-data-bucket'
DATABASE_TO_DEL = 'weather-db'
TABLE_TO_DEL = 'edmonton_weather_data_parquet_tbl'
QUERY_OUTPUT_BUCKET = 's3://weather-data-project-result-query/'

# delete all objects in the bucket
s3_client = boto3.client('s3')

try:
    while True:
        root.info('Listing objects in the bucket...')
        # List objects in the bucket
        objects = s3_client.list_objects(Bucket=BUCKET_TO_DEL)
        content = objects.get('Contents', [])
        
        if not content:
            root.info('No more objects in the bucket.')
            break  # Exit the loop if there are no more objects
        
        for obj in content:
            root.info(f'Deleting object: {obj["Key"]}')
            # Delete each object in the bucket
            s3_client.delete_object(Bucket=BUCKET_TO_DEL, Key=obj['Key'])
except Exception as e:
    root.error(f"An error occurred while deleting objects in the bucket: {str(e)}")
    sys.exit(1)

# drop the table too
client = boto3.client('athena')

try:
    root.info('Starting Athena query to drop the table...')
    queryStart = client.start_query_execution(
        QueryString = f"""
        DROP TABLE IF EXISTS `{DATABASE_TO_DEL}`.`{TABLE_TO_DEL}`;
        """,
        QueryExecutionContext = {
            'Database': f'{DATABASE_TO_DEL}'
        }, 
        ResultConfiguration = { 'OutputLocation': f'{QUERY_OUTPUT_BUCKET}'}
    )
except Exception as e:
    root.error(f"An error occurred while starting the Athena query: {str(e)}")
    sys.exit(1)

# possible states are  'QUEUED'|'RUNNING'|'SUCCEEDED'|'FAILED'|'CANCELLED'

# List of final response states
resp = ["FAILED", "SUCCEEDED", "CANCELLED"]

try:
    while True:
        root.info('Checking the status of the Athena query...')
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
except Exception as e:
    root.error(f"An error occurred while checking the status of the Athena query: {str(e)}")
    sys.exit(1)

root.info('Glue job completed successfully.')
