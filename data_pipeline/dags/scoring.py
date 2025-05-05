from airflow import DAG
from airflow.providers.standard.operators.python import PythonVirtualenvOperator
from datetime import datetime
import os
import sys

os.environ['no_proxy']='*'

if os.path.exists("./dev.txt"):
    env = "dev"
else:
    env = "test"

if env == "dev":
    req_path = "requirements.txt"
else:
    req_path = "/home/sergmir/airflow/dags/requirements.txt"

with open(req_path) as file:
    reqs = file.readlines()

reqs = [i.replace('\n', '') for i in reqs]

def add_folder_sys():
    dags_folder = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(dags_folder)

def generate_data(**kwargs):

    add_folder_sys()

    from scoring_modules import generate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    generate_data.main(run_date=run_date, env=env)

def agg_data(**kwargs):

    add_folder_sys()

    from scoring_modules import aggregate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    aggregate_data.main(run_date=run_date, env=env)

def score_n_load(**kwargs):

    add_folder_sys()

    from scoring_modules import score_n_load_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    score_n_load_data.main(run_date=run_date, env=env)
    


with DAG(
    'scoring_dag',
    schedule='@once',
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['scoring']
) as dag:
    
    generate_data_task = PythonVirtualenvOperator(
        task_id='generate_data',
        python_callable=generate_data,
        requirements=reqs,
        system_site_packages=True,
    )

    agg_data_task = PythonVirtualenvOperator(
        task_id='agg_data',
        python_callable=agg_data,
        requirements=reqs,
        system_site_packages=True,
    )

    score_n_load_task = PythonVirtualenvOperator(
        task_id='score_n_load',
        python_callable=score_n_load,
        requirements=reqs,
        system_site_packages=True,
    )

generate_data_task >> agg_data_task >> score_n_load_task