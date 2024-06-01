<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/0-weather%20.png" style="width:100%; height:10%;" />

<h1 style="text-align: center;"> Edmonton weather AWS serverless Project </h1>

## Introduction
The aim of this project is to build an ETL pipeline that will ingest Edmonton weather data from a weather API using AWS serverless resources and other AWS services (`Aws Lambda`, `AWS Kinesis Firehose`, `AWS Glue`, `AWS S3`, `AWS Athena`) and also monitor the weather condition in Edmonton using `Grafana` as a data visualization tool. 

## Data source
The data source used for this project is **[Open-Meteo](https://open-meteo.com/en/docs)**

The specific API URL endpoint used in this project to get edmonton weather data is **[Edmonton API endpoint](https://api.open-meteo.com/v1/forecast?latitude=53.5501&longitude=-113.4687&current=temperature_2m,is_day,rain,snowfall&temperature_unit=fahrenheit&timezone=auto )**


## DATA ARCHITECTURE
<img src="https://github.com/Joshua-omolewa/edmonton_weather_aws_serverless_project/blob/main/img/architetcure-01.gif" style="width:100%; height:100%;"/>