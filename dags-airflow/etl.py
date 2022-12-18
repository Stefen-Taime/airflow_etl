from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python import PythonOperator
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import os
import sys
import pymysql
from faker import Faker
from datetime import datetime
from faker_vehicle import VehicleProvider
from faker_airtravel import AirTravelProvider
from faker_credit_score import CreditScore


path_tcust_csv = "/tmp/dataset.csv"
email_failed = ""

dag = DAG(
    dag_id="elt",
    description="Pipeline for ETL process from oltp to olap production environments.",
    start_date=days_ago(2),
    schedule_interval=None,
)

username = "root"
password = "myrootpassword"
host = "oltp"
port = "3306"
database = "testdb"

try:
    conn = pymysql.connect(host=host, user=username, passwd=password, db=database, connect_timeout=5)
except pymysql.MySQLError as e:
    sys.exit()

def _populate_mysql():

    faker = Faker()
    faker.add_provider(CreditScore)
    faker.add_provider(VehicleProvider)
    faker.add_provider(AirTravelProvider)

    with conn.cursor() as cur:
        cur.execute("""
         CREATE TABLE IF NOT EXISTS `customers` (
        `id` int NOT NULL AUTO_INCREMENT,
        `name` text,
        `sex` text,
        `adress` text,
        `phone_number` text,
        `email` text,
        `photo` text,
        `birth` date DEFAULT NULL,
        `job` text,
        `dt_update` timestamp NULL DEFAULT NULL,
        PRIMARY KEY (`id`)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS `credit_score` (
        `id` int NOT NULL AUTO_INCREMENT,
        `customer_id` int NOT NULL,
        `name` text,
        `provider` text,
        `credit_score` text,
        `dt_update` timestamp NULL DEFAULT NULL,
        PRIMARY KEY (`id`)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS `flight` (
        `id` int NOT NULL AUTO_INCREMENT,
        `customer_id` int NOT NULL,
        `airport_name` text,
        `linha_aerea` text,
        `airport_iata` text,
        `dt_update` timestamp NULL DEFAULT NULL,
        PRIMARY KEY (`id`)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS `vehicle` (
        `id` int NOT NULL AUTO_INCREMENT,
        `customer_id` int NOT NULL,
        `model_year` text,
        `model` text,
        `manufacturer` text,
        `year_vehicle` int DEFAULT NULL,
        `category` text,
        `dt_update` timestamp NULL DEFAULT NULL,
        PRIMARY KEY (`id`)
        )
        """)

        for i in range(1000):
            name         = faker.name()
            customer_id  = faker.random_int()
            sex         = faker.lexify(text='?', letters='MF')
            adress     = faker.address() 
            phone_number     = faker.phone_number() 
            email        = faker.safe_email() 
            photo         = faker.image_url() 
            birth   = faker.date_of_birth() 
            job    = faker.job() 
            provider     = faker.credit_score_provider() 
            credit_score = faker.credit_score()
            model_year   = faker.vehicle_year_make_model()
            model       = faker.vehicle_make_model() 
            manufacturer   = faker.vehicle_make()
            year_vehicle  = faker.vehicle_year() 
            category    = faker.vehicle_category() 
            airport_name    = faker.airport_name()
            linha_aerea  = faker.airline()
            airport_iata     = faker.airport_iata()
            dt_update    = datetime.now() 

            customers_query = f"insert into customers ( name, sex, adress, phone_number, email, photo, birth, job, dt_update) values('{name}', '{sex}', '{adress}', '{phone_number}', '{email}', '{photo}', '{birth}', '{job}', '{dt_update}')"
            credit_query = f"insert into credit_score ( customer_id, name, provider, credit_score, dt_update) values('{customer_id}', '{name}', '{provider}', '{credit_score}', '{dt_update}')"
            vehicle_query = f"insert into vehicle ( customer_id, model_year, model, manufacturer, year_vehicle, category, dt_update) values('{customer_id}', '{model_year}', '{model}', '{manufacturer}', '{year_vehicle}', '{category}','{dt_update}')"
            flight_query = f"insert into flight ( customer_id, airport_name, linha_aerea, airport_iata, dt_update) values('{customer_id}', '{airport_name}', '{linha_aerea}', '{airport_iata}', '{dt_update}')"

            try:
                cur.execute(flight_query)
                conn.commit()
            except:
                print(f"Error writing flight row with the following values('{customer_id}', '{airport_name}', '{linha_aerea}', '{airport_iata}', '{dt_update}')")
            
            try:
                cur.execute(customers_query)
                conn.commit()
            except:
                print(f"Error writing customer row with the following values('{name}', '{sex}', '{adress}', '{phone_number}', '{email}', '{photo}', '{birth}', '{job}', '{dt_update}')")

            try:
                cur.execute(credit_query)
                conn.commit()
            except:
                print(f"Error writing credit row with the following values('{customer_id}', '{name}', '{provider}', '{credit_score}', '{dt_update}')")

            try:
                cur.execute(vehicle_query)
                conn.commit()
            except:
                print(f"Error writing vehicle row with the following values('{customer_id}', '{model_year}', '{model}', '{manufacturer}', '{year_vehicle}', '{category}','{dt_update}')")
    return "Finished creating Databases and writing rows"




def _extract():
    #connecting to the oltp database.
    engine_mysql_oltp = sqlalchemy.create_engine('mysql+pymysql://root:myrootpassword@oltp:3306/testdb')
    
    #selecting the data.
    dataset_df = pd.read_sql_query(r"""
                        SELECT   cust.id
                        , cust.name
                        , cust.job
                        , cred.credit_score
                        , vehicle.manufacturer 
                        FROM customers cust 
                        INNER JOIN (SELECT id, MAX(credit_score) as credit_score 
                                    FROM credit_score GROUP BY id) 
                        cred ON cred.id = cust.id 
                        INNER JOIN vehicle 
                        ON vehicle.id = cust.id
                        LIMIT 1000"""
                        ,engine_mysql_oltp
    )
    #exporting the data to the stage area.
    dataset_df.to_csv(
        path_tcust_csv,
        index=False
    )

def _transform():
    
    dataset_df = pd.read_csv(path_tcust_csv)

    #transforming the attribute data.
    dataset_df["model"] = dataset_df["manufacturer"]
    
    dataset_df.drop([    "id"
                        ,"manufacturer"
                    ]
                    ,axis=1
                    ,inplace=True)
    
    #persisting the dataset in the tcustorary file
    dataset_df.to_csv(
        path_tcust_csv,
        index=False
    )

def _load():
    #connecting to the postgresql database
    engine_postgresql_olap = sqlalchemy.create_engine('postgresql+psycopg2://postgres:Sup3rS3c3t@olap:5432/testdb')
    
    #selecting the data
    #reading the data from the csv files.
    dataset_df = pd.read_csv(path_tcust_csv)

    #Loading the data into the database.
    dataset_df.to_sql("customers_dataset", engine_postgresql_olap, if_exists="replace",index=False)


populate_Database_task = PythonOperator(
    task_id="populate_oltp", 
    python_callable=_populate_mysql,
    email_on_failure=True,
    email=email_failed, 
    dag=dag
)

extract_task = PythonOperator(
    task_id="Extract_Dataset", 
    python_callable=_extract,
    email_on_failure=True,
    email=email_failed, 
    dag=dag
)    

transform_task = PythonOperator(
    task_id="Transform_Dataset",
    email_on_failure=True,
    email=email_failed, 
    python_callable=_transform, 
    dag=dag
)

load_task = PythonOperator(
    task_id="Load_Dataset",
    email_on_failure=True,
    email=email_failed, 
    python_callable=_load,
    dag=dag
)

clean_task = BashOperator(
    task_id="Clean",
    email_on_failure=True,
    email=email_failed,
    bash_command="scripts/clean.sh",
    dag=dag
)

email_task = EmailOperator(
    task_id="Notify",
    email_on_failure=True,
    email=email_failed, 
    to='',
    subject='Pipeline Finished',
    html_content='<p> The Pipeline for updating data between OLTP and OLAP environments has been successfully completed.<p>',
    dag=dag)

populate_Database_task >> extract_task >> transform_task >> load_task >> clean_task >> email_task
