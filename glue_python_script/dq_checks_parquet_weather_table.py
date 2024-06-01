import sys
import awswrangler as wr # for creating pandas dataframe that interact with AWS services
import logging

# Logging setup
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

TEST_DATABASE = 'weather-db'
TEST_TABLE = 'edmonton_weather_data_parquet_tbl'

# This check counts the number of NULL rows in the temp_C column
# If any rows are NULL, the check returns a number > 0
NULL_DQ_CHECK = f"""
SELECT 
    SUM(CASE WHEN temp_C IS NULL THEN 1 ELSE 0 END) AS total_null_values
FROM "{TEST_DATABASE}"."{TEST_TABLE}"
;
"""

try:
    logging.info('Running quality check query on Athena...')
    # Run the quality check
    df = wr.athena.read_sql_query(sql=NULL_DQ_CHECK, database=TEST_DATABASE) # awswragler with athena allows us to run queries on Athena and fetch the result as a DataFrame
    root.info('Quality check query executed successfully.')

    # Check the result
    total_null_values = df['total_null_values'][0]
    root.info(f'Total NULL values found in temp_C column: {total_null_values}')

    # Exit if we get a result > 0
    if total_null_values > 0:
        root.error('Results returned. Quality check failed.')
        sys.exit('Results returned. Quality check failed.')
    else:
        root.info('Quality check passed.')

except Exception as e:
    root.error(f"An error occurred during the quality check: {str(e)}")
    sys.exit(1)
