# author: Joshua Omolewa
import json
import urllib3
from datetime import datetime
import boto3
import logging
import sys

# Logging setup
root = logging.getLogger()
root.setLevel(logging.INFO)


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

def lambda_handler(event, context):
    # URL to Edmonton API data
    api_url = 'https://api.open-meteo.com/v1/forecast?latitude=53.5501&longitude=-113.4687&current=temperature_2m,is_day,rain,snowfall&temperature_unit=fahrenheit&timezone=auto'
    firehose_stream_name = 'raw-data-01'
    
    http = urllib3.PoolManager()  # creating a manager for handling HTTP connection
    
    try:
        root.info('Sending GET request to the API URL...')
        response = http.request('GET', api_url)  # sending get request to the API URL
        
        if response.status == 200:
            root.info('API request successful.')
            
            # Decode the binary content (bytes) into a string
            content = response.data.decode(encoding='utf-8', errors='strict')
            root.info('Response data decoded.')
            
            # Parse JSON string to a Python dictionary
            data = json.loads(content)
            root.info('Response data parsed to JSON.')
            
            # Formatting the response to fit data I am interested in from the payload
            data_formatted = {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'timezone': data['timezone'],
                'time': data['current']['time'],
                'temperature_fahrenheit': data['current']['temperature_2m'],
                'day_or_night': data['current']['is_day'],
                'rain': data['current']['rain'],
                'snowfall': data['current']['snowfall'],
                'time_processed': str(datetime.now())
            }
            
            root.info(f'Formatted data: {data_formatted}')
            
            # Sending data to Kinesis Firehose
            client = boto3.client('firehose')
            
            # Writing a single data record into an Amazon Firehose delivery stream
            msg = str(data_formatted) + '\n'  # adding new line so Firehose does not need to add new line to separate responses
            
            response = client.put_record(
                DeliveryStreamName=firehose_stream_name,
                Record={
                    'Data': msg
                }
            )
            
            root.info('Data sent to Kinesis Firehose.')
            
        else:
            root.error(f'API request failed with status code: {response.status}')
            return {
                'statusCode': response.status,
                'body': 'API request failed'
            }
        
    except Exception as e:
        root.error(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"An error occurred: {str(e)}"
        }
    
    return {
        'statusCode': 200,
        'sent_data': json.dumps(data_formatted),
        'firehose_response': response
    }
