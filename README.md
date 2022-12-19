# ELT Airflow Pipeline Project

[![Python >= 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

## About

Project using data engineering concepts.

The project is an ELT (Extract, Load, Transform) data pipeline, orchestrated with Apache Airflow through Docker containers.

Faker is used as a package to generate data to a mysql database. The data is extracted from mysql, transformed with pandas and Sql and then loaded into an Olap postgres database. A notification is then sent by email once the whole process is completed.


## Architecture 

![alt text](/images/airflow.png)


## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)


## Setup

Clone the project to your desired location:

    $ git clone https://github.com/Stefen-Taime/airflow_etl.git

fill the AIRFLOW__SMTP__SMTP_USER, AIRFLOW__SMTP__SMTP_PASSWORD, AIRFLOW__SMTP__SMTP_MAIL_FROM in .envExample file:

    AIRFLOW_ADMIN_MAIL=airflow
    AIRFLOW_ADMIN_FIRSTNAME=airflow
    AIRFLOW_ADMIN_NAME=airflow
    AIRFLOW_ADMIN_PASSWORD=airflowpassword
    AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
    AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgres+psycopg2://airflow:airflowpassword@postgres:5432/airflow
    AIRFLOW__CORE__FERNET_KEY=81HqDtbqAywKSOumSha3BhWNOdQ26slT6K0YaZeZyPs=
    AIRFLOW_CONN_METADATA_DB=postgres+psycopg2://airflow:airflowpassword@postgres:5432/airflow
    AIRFLOW_VAR__METADATA_DB_SCHEMA=airflow
    AIRFLOW__SCHEDULER__SCHEDULER_HEARTBEAT_SEC=5
    AIRFLOW__CORE__EXECUTOR=LocalExecutor
    AIRFLOW__SMTP__SMTP_HOST=smtp.mailtrap.io
    AIRFLOW__SMTP__SMTP_PORT=2525
    AIRFLOW__SMTP__SMTP_USER=xxxxxxxxxxx
    AIRFLOW__SMTP__SMTP_PASSWORD=xxxxxxx
    AIRFLOW__SMTP__SMTP_MAIL_FROM=your_email@gmail.com
    AIRFLOW__WEBSERVER__BASE_URL=http://localhost:8080
    POSTGRES_USER=airflow
    POSTGRES_PASSWORD=airflowpassword
    POSTGRES_DB=airflow
    AIRFLOW_UID=1000
    AIRFLOW_GID=0
    AIRFLOW_UID=1000
    AIRFLOW_GID=0
    AIRFLOW_UID=1000
    AIRFLOW_GID=0
    PG_VER=14-alpine
    POSTGRES_SRC_PASSWORD=Sup3rS3c3t
    PORT=5432
    POSTGRES_USER_OLAP=postgres
    HOSTNAME=olap
    ONTAINER_NAME=postgres
    POSTGRES_DB_OLAP=postgres

grant permissions to the bash script:

    chmod a+x build_Services.sh

Build Docker:

    $ docker-compose up --build -d


Start Containers:

    $ docker-compose up -d

When everything is done, you can check all the containers running:

    $ docker ps

## Airflow Interface

Now you can access Airflow web interface by going to http://localhost:8080 with the default user which is in the docker-compose.yml. **Username/Password: airflow/airflowpassword**

## Shut down or restart Airflow

If you need to make changes or shut down:

    $ docker-compose down

## References 

- [Apache Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)
- [Spark by examples](https://sparkbyexamples.com/pyspark-tutorial/)
- [Spark s3 integration](https://spark.apache.org/docs/latest/cloud-integration.html)
- [Airflow and Spark with Docker](https://medium.com/data-arena/building-a-spark-and-airflow-development-environment-with-docker-f0b9b625edd8)