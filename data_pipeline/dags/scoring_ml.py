from airflow import DAG
from airflow.providers.standard.operators.python import ExternalPythonOperator
from datetime import datetime
import os

os.environ['no_proxy']='*'

if os.path.exists("./dev.txt"):
    env = "dev"
else:
    env = "test"

if env == "dev":
    py_venv_path = "~/python_venvs/diploma_venv/bin/python3"
else:
    req_path = "/home/sergmir/py_venv/bin/python3"


def generate_data(**kwargs):

    from scoring_modules import generate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    generate_data.main(run_date=run_date, for_ml=True, env=env)

def agg_data(**kwargs):

    from scoring_modules import aggregate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    aggregate_data.main(run_date=run_date, for_ml=True, env=env)

def mark_data():

    from scoring_modules import mark_data

    mark_data.main(env=env)

def teach_n_load():

    from scoring_modules import teach_n_load_model

    teach_n_load_model.main(env=env)



with DAG(
    'scoring_ml_dag',
    schedule='@once',
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['scoring']
) as dag:
    

    generate_data_task = ExternalPythonOperator(
        task_id='generate_data',
        python_callable=generate_data,
        python=py_venv_path
    )

    agg_data_task = ExternalPythonOperator(
        task_id='agg_data',
        python_callable=agg_data,
        python=py_venv_path
    )

    mark_data_task = ExternalPythonOperator(
        task_id='mark_data',
        python_callable=mark_data,
        python=py_venv_path
    )

    teach_n_load_task = ExternalPythonOperator(
        task_id='teach_n_load_model',
        python_callable=teach_n_load,
        python=py_venv_path
    )

generate_data_task >> agg_data_task >> mark_data_task >> teach_n_load_task