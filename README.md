<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/0-weather%20.png" style="width:100%; height:10%;" />

<h1 style="text-align: center;">  AWS Serverless ETL Project for Edmonton weather data </h1>

## Introduction
The aim of this project is to build an ETL pipeline that will ingest Edmonton weather data from a weather API using AWS serverless resources and other AWS services (`Aws Lambda`, `AWS Eventbridge`, `AWS Kinesis Firehose`, `AWS Glue`, `AWS S3`, `AWS Athena`) and also monitor the weather condition in Edmonton using `Grafana` as a data visualization tool. 

## Data source
The data source used for this project is **[Open-Meteo](https://open-meteo.com/en/docs)**

The specific API URL endpoint used in this project to get edmonton weather data is **[Edmonton API endpoint](https://api.open-meteo.com/v1/forecast?latitude=53.5501&longitude=-113.4687&current=temperature_2m,is_day,rain,snowfall&temperature_unit=fahrenheit&timezone=auto )**


## DATA ARCHITECTURE
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/Animation.gif" style="width:100%; height:100%;"/>

## STEP USED TO COMPLETE THIS PROJECT

* I first queried the API endpoint using my web-browser to get a sense of the data I will be ingesting for my serverles ETL pipeline
#jsonpayload image
* I created all the component (`Aws Lambda`, `AWS Eventbridge`, `AWS Kinesis Firehose`, `AWS Glue (Glue crawler & Glue database called weather-db)`, `AWS S3`, `AWS Athena`) in the data architecture using AWS console and adding all the necessary IAM permissions, policy and roles 
  #aws services image
* The `AWS eventbridge` is used to trigger the pipline every 1 minute so I am able to ingest data every 1 minute. Please note that additional S3 bucket were created for AWS athena to store its query result. I created three S3 bucket to store the raw data, store the transformed intermediate data and the last S3 bucket stores the transfromed production data which passes the data quality check
#s3 bucket image
* **The project workflow as follows:** The AWS eventbridge triggers the lambda function to ingest raw data from the weather API and put the raw data into the AWS Kinesis Firehose Stream which batches the data before loading the raw data in JSON format into the raw S3 bucket. Then we have a Glue workflow shedule to run at a certain time and it consists of several Glue jobs required to process the data and also perform data quality check before publishing the data into the production tables that can be queried using Athena. Grafana can connect using Athena for data visualization.
* The Glue workflow pipeline for the data transformation phase consist of several Glue jobs (please note that all Glue jobs use python shell for execution). The  first glue job crawls the raw data in raw S3 bucket which stores the  json data from kinesis firehouse to create the raw table  in the glue data catalog and then the second glue job delete any old data in the intermediate transformed S3 bucket before doing the transformation for the new raw data. Then after deletion the old transformed parquet data from the intermediate transformed data S3 bucket is complete, the third glue job takes  new raw json data and transforms it  into parquet to meet requirements and stores it in the intermediate transformed S3 bucket. The fourth Glue job query the data in the intermediate S3 bucket using Athena and performes a data quality check  to ensure that the transformed data is valid before publishing the data to the production enviroment  contains snapshot tables  of every run for the data pipeline which is good just incase I need to backfill. The data in the production environtment is partitioned stored in a S3 bucket 