from airflow import DAG
from airflow.providers.standard.operators.python import PythonVirtualenvOperator
from datetime import datetime
import os

os.environ['no_proxy']='*'

if os.path.exists("./dev.txt"):
    env = "dev"
else:
    env = "test"

def generate_data(**kwargs):

    from scoring_modules import generate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    generate_data.main(run_date=run_date, env=env)

def agg_data(**kwargs):

    from scoring_modules import aggregate_data

    run_date = kwargs['logical_date'].strftime("%Y-%m-%d")

    aggregate_data.main(run_date=run_date, env=env)

def score_n_load(**kwargs):

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
    )

    agg_data_task = PythonVirtualenvOperator(
        task_id='agg_data',
        python_callable=agg_data,
    )

    score_n_load_task = PythonVirtualenvOperator(
        task_id='score_n_load',
        python_callable=score_n_load,
    )

generate_data_task >> agg_data_task >> score_n_load_task