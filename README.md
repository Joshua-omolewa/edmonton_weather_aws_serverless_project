<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/0-weather%20.png" style="width:100%; height:10%;" />

<h1 style="text-align: center;">  AWS Serverless ETL Project for Edmonton weather data </h1>

# Author: 👤 **Joshua Omolewa**

## Introduction
The aim of this project is to build an ETL pipeline that will ingest Edmonton weather data from a weather API using AWS serverless resources and other AWS services (`Aws Lambda`, `AWS Eventbridge`, `AWS Kinesis Firehose`, `AWS Glue`, `AWS S3`, `AWS Athena`) and also monitor the weather condition in Edmonton using `Grafana` as a data visualization tool. 

## Data source
The data source used for this project is **[Open-Meteo](https://open-meteo.com/en/docs)**

The specific API URL endpoint used in this project to get edmonton weather data is **[Edmonton API endpoint](https://api.open-meteo.com/v1/forecast?latitude=53.5501&longitude=-113.4687&current=temperature_2m,is_day,rain,snowfall&temperature_unit=fahrenheit&timezone=auto )**


## DATA ARCHITECTURE
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/Animation.gif" style="width:100%; height:100%;"/>

## STEPS USED TO COMPLETE THIS PROJECT

* I first queried the API endpoint using my web-browser to get a sense of the data I will be ingesting for my serverless ETL pipeline
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/1.1-%20weather%20json%20payload.png" style="width:50%; height:50%;"/>

* I created all the component (`Aws Lambda`, `AWS Eventbridge`, `AWS Kinesis Firehose`, `AWS Glue (Glue crawler & Glue database called weather-db)`, `AWS S3`, `AWS Athena`) in the data architecture using AWS console and adding all the necessary IAM permissions, policy and roles. The Glue crawler points to the S3 bucket that will contain the raw data. Also, I created a database in Glue to contain all tables for this project
  
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/AWS_services.png" style="width:100%; height:100%;"/>

* The `AWS eventbridge` is used to trigger the pipline every 1 minute so I am able to ingest data every 1 minute. Please note that additional S3 bucket were created for AWS athena to store its query result. I created three S3 bucket to store the raw data, store the transformed intermediate data and the last S3 bucket stores the transfromed production data which passes the data quality check
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/S3%20buckets.png" style="width:100%; height:100%;"/>

* **The project workflow is as follows:** The AWS eventbridge triggers the  **[lambda function](https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/aws_lambda_script/lambda_function.py)** to ingest raw data from the weather API and put the raw data into the AWS Kinesis Firehose Stream which batches the data before loading the raw data in JSON format into the raw S3 bucket. Then we have a Glue workflow shedule to run at a certain time and it consists of several Glue jobs required to process the data and also perform data quality check before publishing the data into the production tables that can be queried using Athena. Grafana can connect using Athena for data visualization. Cloud Watch enabled real time access to the data pipeline logs
* The Glue workflow pipeline (please see image below) for the data transformation phase consist of several Glue jobs (please note that all Glue jobs use python shell for execution). The  first glue job crawls the raw data in raw S3 bucket which stores the  json data from kinesis firehouse to create the raw table  in the glue data catalog and then the  **[second glue job](https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/glue_python_script/delete_raw_parquet_weather_table_s3_athena.py)** delete any old data in the intermediate transformed S3 bucket before doing the transformation for the new raw data. Then after deletion the old transformed parquet data from the intermediate transformed data S3 bucket is complete, the  **[third glue job](https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/glue_python_script/create_parquet_partitioned_weather_table_glue_job.py)** takes  new raw json data and transforms it  into parquet to meet requirements and stores it in the intermediate transformed S3 bucket. The  **[fourth Glue job](https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/glue_python_script/dq_checks_parquet_weather_table.py)** query the data in the intermediate S3 bucket using Athena and performes a data quality check  to ensure that the transformed data is valid before publishing the data to the production enviroment which is done by the  **[fifth Glue job](https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/glue_python_script/publish_prod_parquet_weather_table.py)**  and contains snapshot tables  of every run for the data pipeline which is good just incase I need to backfill. The data in the production environtment is partitioned stored in a S3 bucket. The image below shows the glue workflow.
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/14-%20pipline%20flow.png" style="width:100%; height:100%;"/>

* Once the Glue workflow jobs are completed, it creates a new table as a snapshot with timestamps so I can always backfill incase of corrupt data. See image below to see completion image for Glue workflow and the production tables
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/success-%20workflow%20glue.png" style="width:100%; height:100%;"/>

<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/prod%20table%20samples.png" style="width:100%; height:100%;"/>

* Finally, I created a dashboard for data visualization using Grafana to monitor the weather condition in Canada. You can find the dashboard **[here](https://omolewajoshua.grafana.net/dashboard/snapshot/fPmxgqHjCmCOhXrKnB2ZJiO0Opdvxb56?orgId=1)**
  
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/Grafana%20Dashboard.png" style="width:100%; height:100%;"/>

# Follow Me On
  
* LinkedIn: [@omolewajoshua](https://www.linkedin.com/in/joshuaomolewa/)  
* Github: [@joshua-omolewa](https://github.com/Joshua-omolewa)

## Show your support

Give a ⭐️ if this project helped you!