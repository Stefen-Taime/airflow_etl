FROM apache/airflow:2.5.0
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ARG AIRFLOW_HOME=/opt/airflow 

#ADD dags-airflow /opt/airflow/dags 

ADD airflow.cfg /opt/airflow/airflow.cfg

RUN chown -R "airflow:root" /opt/airflow/  

USER airflow 

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org boto3

# USER ${AIRFLOW_UID}
USER airflow

ADD requirements.txt /requirements.txt


RUN python -m pip install Faker
RUN python -m pip install faker_airtravel
RUN python -m pip install faker-credit-score
RUN python -m pip install faker-vehicle


RUN pip install -r /requirements.txt